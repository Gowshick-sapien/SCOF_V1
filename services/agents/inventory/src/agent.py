"""Inventory Agent Implementation."""

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
    NUMPY_SEED,
    PYTHON_RANDOM_SEED,
    REORDER_POINT_DAYS,
    SAFETY_STOCK_THRESHOLD_DAYS,
    XGBOOST_SEED,
)
from .data_access import InventoryDataAccess
from .features import InventoryFeatureBuilder
from .mcp.tools import INVENTORY_MCP_TOOLS
from .models.ensemble import InventoryEnsemble
from .models.statistical_model import InventoryStatisticalInference, InventoryStatisticalTrainer
from scof_shared.knowledge import Neo4jGraphClient, PgVectorClient
from .models.xgboost_model import InventoryXGBoostInference, InventoryXGBoostTrainer


class InventoryAgent(BaseAgent):
    """Specialist AI Agent for Inventory Management and Stockout Risk Assessment."""

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
        self.data_access = InventoryDataAccess(db_config=db_config)
        self.feature_builder = InventoryFeatureBuilder()
        self._init_models()

    def _init_models(self) -> None:
        """Fits or loads trained models and registers them in the ensemble."""
        np.random.seed(NUMPY_SEED)

        weights = {"xgboost": 0.6, "statistical": 0.4}
        if self.config and self.config.ensemble_weights:
            weights = self.config.ensemble_weights

        self.ensemble = InventoryEnsemble(weights=weights)

        dummy_df, _ = self.data_access.get_inventory_levels()
        X, y, _ = self.feature_builder.build_features(dummy_df, [])

        xgb_trainer = InventoryXGBoostTrainer(seed=XGBOOST_SEED)
        xgb_art = xgb_trainer.fit(X, y)
        self.ensemble.register_model("xgboost", InventoryXGBoostInference(xgb_art))

        stat_trainer = InventoryStatisticalTrainer()
        stat_art = stat_trainer.fit(X, y)
        self.ensemble.register_model("statistical", InventoryStatisticalInference(stat_art))

    def get_agent_card(self, endpoint_url: str = "http://localhost:8012") -> AgentCard:
        tool_names = [t.name for t in INVENTORY_MCP_TOOLS]
        return AgentCard(
            agent_id=self.agent_id,
            name=AGENT_NAME,
            description="Inventory agent microservice assessing stock levels, depletion rates, safety stock breaches, and stockout risks.",
            version="1.0.0",
            capabilities=["stockout_risk_assessment", "safety_stock_monitoring", "inventory_projection"],
            tags=["inventory", "stockout", "safety-stock"],
            supported_contexts=["supplier_delay", "stockout_risk", "reorder_recommendation"],
            dependencies=["postgres", "neo4j"],
            input_schema={"context": "ScenarioContext"},
            output_schema="StructuredClaim",
            protocol="A2A/1.0",
            endpoint=endpoint_url,
        )

    def analyze(self, context: ScenarioContext) -> StructuredClaim:
        """Executes inventory risk analysis and returns StructuredClaim."""
        inv_df, inv_qhash = self.data_access.get_inventory_levels(
            run_id=context.run_id,
            warehouse_ids=context.warehouse_ids,
            product_ids=context.product_ids,
        )
        disruptions, disr_qhash = self.data_access.get_supplier_disruptions(
            run_id=context.run_id,
            scenario_id=context.scenario_id,
        )

        X, y, f_names = self.feature_builder.build_features(inv_df, disruptions)
        ensemble_res = self.ensemble.predict(X)

        current_stock = float(X[-1, 0]) if len(X) > 0 else 500.0
        depletion_rate = float(X[-1, 1]) if len(X) > 0 else 15.0
        days_of_supply = float(X[-1, 2]) if len(X) > 0 else 30.0

        projected_7d_stock = float(np.mean(ensemble_res.point_forecast))

        # Calculate composite confidence score
        interval_width = float(np.mean(ensemble_res.interval.upper - ensemble_res.interval.lower))
        conf_score_obj = self.ensemble.confidence_calculator.compute(
            agreement_score=ensemble_res.agreement_score,
            interval_width=interval_width,
            historical_error=0.10,
            max_interval_width=100.0,
        )
        raw_confidence = conf_score_obj.score

        supplier_delays = [d for d in disruptions if d.get("disruption_type") == "supplier_delay"]
        has_delay = len(supplier_delays) > 0

        # Rule evaluation for stockout risk
        if days_of_supply <= SAFETY_STOCK_THRESHOLD_DAYS or projected_7d_stock <= 80.0 or has_delay:
            rec = "Issue expedited purchase reorder and reroute safety stock from alternate warehouse."
            reasoning = f"Stock level depleting at {depletion_rate:.1f} units/day. Days of supply ({days_of_supply:.1f} days) is critical. "
            if has_delay:
                reasoning += f"Active supplier delay disruption detected for target entity {supplier_delays[0].get('target_entity_id')}. "
            reasoning += f"Projected 7-day stock is {projected_7d_stock:.1f} units. Model agreement: {ensemble_res.agreement_score:.2f}."
            priority = "HIGH"
            impact = "High risk of stockout within 5 days leading to unfulfilled customer demand."
        elif days_of_supply <= REORDER_POINT_DAYS:
            rec = "Place standard replenishment order with primary supplier."
            reasoning = f"Inventory level reached reorder point ({days_of_supply:.1f} days of supply remaining). Projected 7-day stock level: {projected_7d_stock:.1f} units."
            priority = "MEDIUM"
            impact = "Moderate depletion rate requires standard replenishment."
        else:
            rec = "Inventory stock levels healthy. Maintain current reorder strategy."
            reasoning = f"Inventory stock levels sufficient ({days_of_supply:.1f} days of supply remaining). Projected 7-day stock level: {projected_7d_stock:.1f} units."
            priority = "LOW"
            impact = "Stock levels operating within optimal parameters."

        builder = ClaimBuilder(agent_id=self.agent_id, scenario_id=context.scenario_id)
        builder.set_recommendation(rec)
        builder.set_reasoning(reasoning)
        builder.set_confidence(raw_confidence)
        builder.set_priority(priority)
        builder.set_impact(impact)

        # Add traceable evidence
        builder.add_evidence(
            type="historical_data",
            source="PostgreSQL: inventory_levels",
            summary=f"Current stock on hand: {current_stock:.1f} units. Depletion rate: {depletion_rate:.1f} units/day ({days_of_supply:.1f} days of supply).",
            reference_id=f"inventory_level:{context.scenario_id}",
            query_hash=inv_qhash,
        )

        builder.add_evidence(
            type="model_output",
            source="InventoryEnsemble (XGBoost + Statistical)",
            summary=f"Ensemble projected 7-day stock: {projected_7d_stock:.1f} units. Agreement score: {ensemble_res.agreement_score:.2f}.",
            reference_id=f"inventory_forecast:{context.scenario_id}",
        )

        if disruptions:
            builder.add_evidence(
                type="external_signal",
                source="PostgreSQL: disruption_events",
                summary=f"Active disruptions affecting inventory: {len(disruptions)} events.",
                reference_id=f"disruption:{context.scenario_id}",
                query_hash=disr_qhash,
            )

        return builder.build(confidence_floor=self.confidence_floor)
