"""Demand Agent Implementation."""

from pathlib import Path
from typing import Optional
import numpy as np
from scof_shared.agent_base.base_agent import BaseAgent
from scof_shared.agent_base.claim_builder import ClaimBuilder
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim

from .config import (
    AGENT_ID,
    AGENT_NAME,
    MODEL_ARTIFACT_DIR,
    NUMPY_SEED,
    PYTHON_RANDOM_SEED,
    XGBOOST_SEED,
)
from .data_access import DemandDataAccess
from .features import DemandFeatureBuilder
from .mcp.tools import DEMAND_MCP_TOOLS
from .models.ensemble import DemandEnsemble
from .models.statistical_model import DemandStatisticalInference, DemandStatisticalTrainer
from scof_shared.knowledge import Neo4jGraphClient, PgVectorClient
from .models.xgboost_model import DemandXGBoostInference, DemandXGBoostTrainer


class DemandAgent(BaseAgent):
    """Specialist AI Agent for Demand Forecasting."""

    def __init__(
        self,
        profile_path: Optional[str] = None,
        db_config: Optional[dict] = None,
        graph_client: Optional[Neo4jGraphClient] = None,
        vector_client: Optional[PgVectorClient] = None,
    ):
        super().__init__(
            agent_id=AGENT_ID,
            profile_path=profile_path,
            graph_client=graph_client,
            vector_client=vector_client,
        )
        self.data_access = DemandDataAccess(db_config=db_config)
        self.feature_builder = DemandFeatureBuilder()
        self._init_models()

    def _init_models(self) -> None:
        """Fits or loads trained models and registers them in the ensemble."""
        # Set seeds for determinism
        np.random.seed(NUMPY_SEED)

        weights = {"xgboost": 0.6, "statistical": 0.4}
        if self.config and self.config.ensemble_weights:
            weights = self.config.ensemble_weights

        self.ensemble = DemandEnsemble(weights=weights)

        # Fit models on baseline synthetic data
        dummy_df, _ = self.data_access.get_historical_demand(limit_days=30)
        X, y, _ = self.feature_builder.build_features(dummy_df, [])

        xgb_trainer = DemandXGBoostTrainer(seed=XGBOOST_SEED)
        xgb_art = xgb_trainer.fit(X, y)
        self.ensemble.register_model("xgboost", DemandXGBoostInference(xgb_art))

        stat_trainer = DemandStatisticalTrainer()
        stat_art = stat_trainer.fit(X, y)
        self.ensemble.register_model("statistical", DemandStatisticalInference(stat_art))

    def get_agent_card(self, endpoint_url: str = "http://localhost:8011") -> AgentCard:
        tool_names = [t.name for t in DEMAND_MCP_TOOLS]
        return AgentCard(
            agent_id=self.agent_id,
            name=AGENT_NAME,
            description="Ensemble-based demand forecasting microservice evaluating order history and active disruptions.",
            version="1.0.0",
            capabilities=["demand_forecasting", "trend_analysis", "disruption_impact_assessment"],
            tags=["forecasting", "demand", "time-series"],
            supported_contexts=["demand_spike", "baseline_forecast"],
            dependencies=["postgres", "neo4j"],
            input_schema={"context": "ScenarioContext"},
            output_schema="StructuredClaim",
            protocol="A2A/1.0",
            endpoint=endpoint_url,
        )

    def analyze(self, context: ScenarioContext) -> StructuredClaim:
        """Executes demand forecast analysis and returns StructuredClaim."""
        demand_df, demand_qhash = self.data_access.get_historical_demand(
            run_id=context.run_id,
            product_ids=context.product_ids,
        )
        disruptions, disr_qhash = self.data_access.get_active_disruptions(
            run_id=context.run_id,
            scenario_id=context.scenario_id,
        )

        X, y, f_names = self.feature_builder.build_features(demand_df, disruptions)
        ensemble_res = self.ensemble.predict(X)

        avg_predicted = float(np.mean(ensemble_res.point_forecast))
        recent_actual = float(np.mean(y[-7:])) if len(y) >= 7 else float(np.mean(y))

        pct_change = ((avg_predicted - recent_actual) / max(1.0, recent_actual)) * 100.0

        # Calculate composite confidence score
        interval_width = float(np.mean(ensemble_res.interval.upper - ensemble_res.interval.lower))
        conf_score_obj = self.ensemble.confidence_calculator.compute(
            agreement_score=ensemble_res.agreement_score,
            interval_width=interval_width,
            historical_error=0.15,
            max_interval_width=100.0,
        )
        raw_confidence = conf_score_obj.score

        # Determine recommendation, reasoning, priority, impact
        has_spike = any(d.get("disruption_type") == "demand_spike" for d in disruptions)

        if has_spike or pct_change > 20.0:
            rec = f"Increase production and safety stock buffer by {int(abs(pct_change))}% for product allocation."
            reasoning = f"Demand forecast projects a {pct_change:.1f}% surge over trailing baseline. Active demand spike disruption detected. Forecast ensemble agreement is {ensemble_res.agreement_score:.2f}."
            priority = "HIGH"
            impact = f"Potential stockout risk if inventory allocations are not increased by {int(abs(pct_change))}%."
        else:
            rec = "Maintain current production schedule and inventory reorder parameters."
            reasoning = f"Demand remains stable with projected variation of {pct_change:.1f}%. Forecast interval width is {interval_width:.1f} units."
            priority = "LOW"
            impact = "Normal operational parameters maintained."

        builder = ClaimBuilder(agent_id=self.agent_id, scenario_id=context.scenario_id)
        builder.set_recommendation(rec)
        builder.set_reasoning(reasoning)
        builder.set_confidence(raw_confidence)
        builder.set_priority(priority)
        builder.set_impact(impact)

        # Add traceable evidence
        builder.add_evidence(
            type="historical_data",
            source="PostgreSQL: order_items",
            summary=f"Historical demand sample over {len(demand_df)} records. Recent average: {recent_actual:.1f} units/day.",
            reference_id=f"demand_history:{context.scenario_id}",
            query_hash=demand_qhash,
        )

        builder.add_evidence(
            type="model_output",
            source="DemandEnsemble (XGBoost + Statistical)",
            summary=f"Ensemble point forecast average: {avg_predicted:.1f} units/day. Agreement: {ensemble_res.agreement_score:.2f}.",
            reference_id=f"ensemble_forecast:{context.scenario_id}",
        )

        if disruptions:
            builder.add_evidence(
                type="external_signal",
                source="PostgreSQL: disruption_events",
                summary=f"Active disruptions detected: {len(disruptions)} events.",
                reference_id=f"disruption:{context.scenario_id}",
                query_hash=disr_qhash,
            )

        return builder.build(confidence_floor=self.confidence_floor)
