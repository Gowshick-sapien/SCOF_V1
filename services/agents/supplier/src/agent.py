"""Supplier Intelligence Agent Implementation."""

from typing import Any, Dict, List, Optional
import numpy as np
from scof_shared.agent_base.base_agent import BaseAgent
from scof_shared.agent_base.claim_builder import ClaimBuilder
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim

from scof_shared.knowledge import Neo4jGraphClient, PgVectorClient

from src.config import (
    AGENT_ID,
    AGENT_NAME,
    HIGH_RELIABILITY_THRESHOLD,
    LOW_RELIABILITY_THRESHOLD,
    NUMPY_SEED,
    PYTHON_RANDOM_SEED,
    SKLEARN_SEED,
)
from src.data_access import SupplierDataAccess
from src.features import SupplierFeatureBuilder
from src.mcp.tools import SUPPLIER_MCP_TOOLS
from src.models.ensemble import SupplierEnsemble
from src.models.reliability_scorer import ReliabilityScorerInference, ReliabilityScorerTrainer
from src.models.rule_scorer import RuleScorerInference, RuleScorerInitializer


class SupplierAgent(BaseAgent):
    """Specialist AI Agent for Supplier Intelligence, Vendor Reliability Scoring, and Failure Mitigation."""

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
        self.data_access = SupplierDataAccess(db_config=db_config, graph_client=graph_client)
        self.feature_builder = SupplierFeatureBuilder()
        self._init_models()

    def _init_models(self) -> None:
        """Fits or loads trained models and registers them in the ensemble."""
        np.random.seed(NUMPY_SEED)

        weights = {"reliability_scorer": 0.6, "rule_scorer": 0.4}
        if self.config and self.config.ensemble_weights:
            weights = self.config.ensemble_weights

        self.ensemble = SupplierEnsemble(weights=weights)

        # Baseline synthetic delivery data for model training
        dummy_df, _ = self.data_access.get_supplier_delivery_history()
        dummy_graph, _ = self.data_access.get_supplier_graph_data()
        X, y, _ = self.feature_builder.build_features(
            dummy_df,
            disruptions=[],
            graph_data=dummy_graph,
            alternates_map={"sup-01": 2, "sup-02": 2, "sup-03": 1, "sup-04": 0, "sup-05": 0},
            hop_counts_map={"sup-01": 2, "sup-02": 3, "sup-03": 2, "sup-04": 4, "sup-05": 3},
        )

        # Train GradientBoosting classifier
        ml_trainer = ReliabilityScorerTrainer(seed=SKLEARN_SEED)
        ml_art = ml_trainer.fit(X, y)
        self.ensemble.register_model("reliability_scorer", ReliabilityScorerInference(ml_art))

        # Initialize Rule Scorer
        rule_trainer = RuleScorerInitializer()
        rule_art = rule_trainer.fit(X, y)
        self.ensemble.register_model("rule_scorer", RuleScorerInference(rule_art))

    def get_agent_card(self, endpoint_url: str = "http://localhost:8013") -> AgentCard:
        tool_names = [t.name for t in SUPPLIER_MCP_TOOLS]
        return AgentCard(
            agent_id=self.agent_id,
            name=AGENT_NAME,
            description="Supplier Intelligence agent scoring vendor reliability, predicting supplier failure risks, and recommending backup sourcing via graph queries.",
            version="1.0.0",
            capabilities=["supplier_reliability_scoring", "failure_prediction", "alternate_supplier_recommendation"],
            tags=["supplier", "reliability", "graph"],
            supported_contexts=["supplier_delay", "factory_shutdown", "baseline_assessment"],
            dependencies=["postgres", "neo4j"],
            input_schema={"context": "ScenarioContext"},
            output_schema="StructuredClaim",
            protocol="A2A/1.0",
            endpoint=endpoint_url,
        )

    def rank_alternate_suppliers(
        self,
        alternates: List[Dict[str, Any]],
        supplier_reliabilities: Optional[Dict[str, float]] = None,
        hop_counts: Optional[Dict[str, int]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Ranks alternate suppliers deterministically based on composite score:
        0.40 * reliability + 0.30 * (1 - norm_lead_time) + 0.20 * (1 - norm_unit_cost) + 0.10 * (1 / hops).
        """
        reliabilities = supplier_reliabilities or {}
        hops_map = hop_counts or {}

        scored_candidates = []
        for alt in alternates:
            alt_id = alt.get("alt_supplier_id", "")
            rel = reliabilities.get(alt_id, 0.90)
            lead_time = float(alt.get("alt_lead_time_days", alt.get("lead_time_days", 7.0)))
            unit_cost = float(alt.get("alt_unit_cost", alt.get("unit_cost", 25.0)))
            hops = float(hops_map.get(alt_id, 2))

            norm_lead_time = min(1.0, max(0.0, lead_time / 30.0))
            norm_unit_cost = min(1.0, max(0.0, unit_cost / 100.0))
            hop_factor = 1.0 / max(1.0, hops)

            composite_score = (
                0.40 * rel
                + 0.30 * (1.0 - norm_lead_time)
                + 0.20 * (1.0 - norm_unit_cost)
                + 0.10 * hop_factor
            )

            scored_candidates.append({
                **alt,
                "composite_rank_score": round(composite_score, 4),
                "assessed_reliability": round(rel, 3),
            })

        scored_candidates.sort(key=lambda x: x["composite_rank_score"], reverse=True)
        return scored_candidates

    def analyze(self, context: ScenarioContext) -> StructuredClaim:
        """Executes supplier reliability analysis and returns StructuredClaim."""
        target_supplier = None
        if context.target_entity_type == "supplier" and context.target_entity_id:
            target_supplier = context.target_entity_id

        supplier_ids = [target_supplier] if target_supplier else None

        # Fetch delivery history from Postgres
        delivery_df, delivery_qhash = self.data_access.get_supplier_delivery_history(
            run_id=context.run_id,
            supplier_ids=supplier_ids,
        )

        # Fetch active disruptions
        disruptions, disr_qhash = self.data_access.get_supplier_disruptions(
            run_id=context.run_id,
            scenario_id=context.scenario_id,
        )

        # Inject context disruption if present and not yet in query results
        if context.disruption_type in ["supplier_delay", "factory_shutdown"]:
            context_disr = {
                "disruption_type": context.disruption_type,
                "target_entity_type": context.target_entity_type or "supplier",
                "target_entity_id": context.target_entity_id or "sup-02",
                "severity": context.severity or 3,
            }
            if not any(d.get("target_entity_id") == context_disr["target_entity_id"] for d in disruptions):
                disruptions.append(context_disr)

        # Target product
        target_product = context.product_ids[0] if context.product_ids else "prod-101"

        # Fetch graph data and alternates
        graph_data, graph_qhash = self.data_access.get_supplier_graph_data(
            supplier_id=target_supplier,
            product_id=target_product,
        )

        alternates: List[Dict[str, Any]] = []
        alt_qhash = ""
        if target_supplier:
            alternates, alt_qhash = self.data_access.get_alternate_suppliers(
                supplier_id=target_supplier,
                product_id=target_product,
            )

        # Build feature mappings
        unique_suppliers = list(delivery_df["supplier_id"].unique()) if not delivery_df.empty else [target_supplier or "sup-01"]
        alternates_map = {}
        hop_counts_map = {}
        for s_id in unique_suppliers:
            alts, _ = self.data_access.get_alternate_suppliers(s_id, target_product)
            alternates_map[s_id] = len(alts)
            hops, _ = self.data_access.get_supplier_hop_count(s_id)
            hop_counts_map[s_id] = hops

        # Build feature matrix
        X, y, f_names = self.feature_builder.build_features(
            delivery_df=delivery_df,
            disruptions=disruptions,
            graph_data=graph_data,
            alternates_map=alternates_map,
            hop_counts_map=hop_counts_map,
        )

        # Run ensemble inference
        ensemble_res = self.ensemble.predict(X)
        mean_score = float(np.mean(ensemble_res.point_forecast))
        interval_width = float(np.mean(ensemble_res.interval.upper - ensemble_res.interval.lower))
        conf_obj = self.ensemble.confidence_calculator.compute(
            agreement_score=ensemble_res.agreement_score,
            interval_width=interval_width,
            historical_error=0.10,
            max_interval_width=1.0,
        )
        confidence = float(conf_obj.score)

        # Rank alternates if target supplier is in disruption or low reliability
        is_disrupted = (
            context.disruption_type in ["supplier_delay", "factory_shutdown"]
            or mean_score < LOW_RELIABILITY_THRESHOLD
        )

        # Map supplier reliabilities for ranking
        supplier_reliabilities = {}
        for idx, s_id in enumerate(unique_suppliers):
            if idx < len(ensemble_res.point_forecast):
                supplier_reliabilities[s_id] = float(ensemble_res.point_forecast[idx])
            else:
                supplier_reliabilities[s_id] = 0.90

        ranked_alternates = self.rank_alternate_suppliers(
            alternates=alternates,
            supplier_reliabilities=supplier_reliabilities,
            hop_counts=hop_counts_map,
        )

        # Construct Claim
        target_name = target_supplier or "Network Suppliers"
        if is_disrupted:
            priority = "HIGH"
            if ranked_alternates:
                best_alt = ranked_alternates[0]
                alt_name = best_alt.get("alt_supplier_name", best_alt.get("alt_supplier_id", "alternate"))
                alt_id = best_alt.get("alt_supplier_id", "alt-01")
                lead_days = best_alt.get("alt_lead_time_days", 7)
                recommendation = f"Reroute order volume from disrupted supplier {target_name} to top-ranked alternate {alt_name} ({alt_id}) with {lead_days}-day lead time."
                reasoning = (
                    f"Primary supplier {target_name} reliability score dropped to {mean_score:.2f} under active disruption "
                    f"'{context.disruption_type}' (severity {context.severity or 3}). "
                    f"Neo4j lineage analysis identified {len(ranked_alternates)} qualified alternate supplier(s). "
                    f"Top candidate {alt_name} exhibits {best_alt.get('assessed_reliability', 0.90):.2f} reliability with composite rank score {best_alt.get('composite_rank_score', 0.0):.2f}."
                )
            else:
                recommendation = f"Expedite backup safety stock and initiate emergency procurement for supplier {target_name}."
                reasoning = (
                    f"Primary supplier {target_name} reliability score dropped to {mean_score:.2f} due to '{context.disruption_type}'. "
                    f"No direct alternate suppliers exist in the graph catalog for product {target_product}."
                )
            impact = "Mitigates critical component stockout risk and prevents assembly line interruption."
        else:
            priority = "LOW" if mean_score >= HIGH_RELIABILITY_THRESHOLD else "MEDIUM"
            recommendation = f"Maintain standard procurement schedules with {target_name}."
            reasoning = (
                f"Supplier {target_name} demonstrates stable delivery performance with reliability score {mean_score:.2f} "
                f"across {len(delivery_df)} historical purchase orders. No active supplier disruptions detected."
            )
            impact = "Ensures steady component delivery within nominal lead time tolerances."

        # Check confidence floor
        floor = self.config.confidence_floor if self.config else 0.55
        floor = self.config.confidence_floor if self.config else 0.55

        builder = ClaimBuilder(
            agent_id=self.agent_id,
            scenario_id=context.scenario_id or "scen-default",
        )
        builder.set_recommendation(recommendation)
        builder.set_reasoning(reasoning)
        builder.set_confidence(confidence)
        builder.set_priority(priority)
        builder.set_impact(impact)

        # Evidence Items
        builder.add_evidence(
            type="graph_query",
            source="Neo4j: (Supplier)-[:SUPPLIES]->(Product)",
            summary=f"Graph lineage query for product {target_product} returned {len(graph_data)} supplier-product relationships.",
            reference_id=f"supplier_graph:{target_supplier or 'all'}",
            query_hash=graph_qhash,
        )
        builder.add_evidence(
            type="historical_data",
            source="PostgreSQL: purchase_orders & shipments",
            summary=f"Historical delivery performance records for {len(unique_suppliers)} supplier(s).",
            reference_id=f"delivery_history:{target_supplier or 'all'}",
            query_hash=delivery_qhash,
        )
        builder.add_evidence(
            type="model_output",
            source="SupplierEnsemble (GradientBoosting + RuleScorer)",
            summary=f"Ensemble reliability score: {mean_score:.3f}. Agreement score: {ensemble_res.agreement_score:.3f}.",
            reference_id=f"reliability_ensemble:{context.scenario_id or 'default'}",
        )

        return builder.build(confidence_floor=floor)
