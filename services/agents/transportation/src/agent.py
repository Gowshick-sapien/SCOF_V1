"""Transportation Agent implementation for SCOF.

Analyzes transit delays, evaluates route risks, and formulates carrier rerouting claims.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from scof_shared.agent_base.base_agent import BaseAgent
from scof_shared.agent_base.claim_builder import ClaimBuilder
from scof_shared.schemas.agent_card import AgentCard
from scof_shared.schemas.scenario_context import ScenarioContext
from scof_shared.schemas.structured_claim import StructuredClaim
from scof_shared.knowledge import Neo4jGraphClient, PgVectorClient
from .config import TransportAgentConfig, get_config
from .data_access import TransportDataAccess
from .features import TransportFeatureBuilder
from .models.ensemble import TransportEnsemble, create_trained_transport_ensemble


# Disruption thresholds
DELAY_WARNING_DAYS = 2.0
DELAY_CRITICAL_DAYS = 4.0


class TransportAgent(BaseAgent):
    """SCOF Agent specialized in transportation delays, route risk, and carrier rerouting."""

    def __init__(
        self,
        profile_path: Optional[str] = None,
        config: Optional[TransportAgentConfig] = None,
        data_access: Optional[TransportDataAccess] = None,
        ensemble: Optional[TransportEnsemble] = None,
        db_config: Optional[dict] = None,
        graph_client: Optional[Neo4jGraphClient] = None,
        vector_client: Optional[PgVectorClient] = None,
    ):
        self.transport_config = config or get_config()
        super().__init__(
            agent_id=self.transport_config.agent_id,
            profile_path=profile_path,
            graph_client=graph_client,
            vector_client=vector_client,
        )
        self.data_access = data_access or TransportDataAccess(
            db_config=db_config,
            graph_client=graph_client,
        )
        self.feature_builder = TransportFeatureBuilder()

        # Initialize or train default ensemble
        if ensemble is not None:
            self.ensemble = ensemble
        else:
            mock_shipments, _ = self.data_access.get_shipment_delivery_history()
            mock_routes, _ = self.data_access.get_route_graph_data()
            X_init, y_init, _ = self.feature_builder.build_features(
                shipment_df=mock_shipments,
                route_details=mock_routes,
            )
            seed = getattr(self.transport_config, "seed", 42)
            weights = (
                getattr(self.config, "ensemble_weights", None)
                or getattr(self.transport_config, "ensemble_weights", None)
                or {"delay_predictor": 0.6, "route_scorer": 0.4}
            )
            self.ensemble = create_trained_transport_ensemble(
                X_train=X_init,
                y_train=y_init,
                seed=seed,
                weights=weights,
            )

    def get_agent_card(self, endpoint_url: str = "http://localhost:8014") -> AgentCard:
        """Returns standard metadata AgentCard for discovery."""
        name = getattr(self.config, "name", getattr(self.transport_config, "name", "Transportation Intelligence Agent"))
        version = getattr(self.config, "version", getattr(self.transport_config, "version", "1.0.0"))
        return AgentCard(
            agent_id=self.agent_id,
            name=name,
            version=version,
            description="Predicts shipment delays, scores transport routes, and recommends alternate carrier corridors.",
            capabilities=["delay_prediction", "route_risk_scoring", "alternate_route_recommendation"],
            tags=["transportation", "logistics", "delay", "routes"],
            supported_contexts=["port_congestion", "weather_delay", "canal_blockage", "carrier_strike"],
            dependencies=["postgres", "neo4j"],
            input_schema={"context": "ScenarioContext"},
            output_schema="StructuredClaim",
            protocol="A2A/1.0",
            endpoint=endpoint_url,
        )

    def rank_alternate_routes(
        self,
        alternates: List[Dict[str, Any]],
        carrier_delays: Optional[Dict[str, float]] = None,
    ) -> List[Dict[str, Any]]:
        """Ranks alternate routes using deterministic multi-criteria scoring.

        Composite Score Formula:
            0.40 * reliability + 0.30 * (1 - norm_transit_time) + 0.20 * (1 - norm_cost) + 0.10 * (1 / hops)
        """
        carrier_delays = carrier_delays or {}
        scored_alternates = []

        for alt in alternates:
            carrier = alt.get("alt_carrier", alt.get("carrier", "Unknown"))
            
            raw_rel = alt.get("alt_reliability_rating")
            if raw_rel is None:
                raw_rel = alt.get("reliability_rating")
            if raw_rel is None:
                raw_rel = alt.get("reliability_score")
            rel = float(raw_rel) if raw_rel is not None else 0.90

            raw_transit = alt.get("alt_transit_time_days")
            if raw_transit is None:
                raw_transit = alt.get("transit_time_days")
            transit_days = float(raw_transit) if raw_transit is not None else 5.0

            raw_cost = alt.get("alt_cost")
            if raw_cost is None:
                raw_cost = alt.get("cost")
            cost = float(raw_cost) if raw_cost is not None else 1000.0

            raw_hops = alt.get("hop_count")
            hops = max(1, int(raw_hops)) if raw_hops is not None else 1

            # Adjust reliability if predicted delay is known for this carrier
            if carrier in carrier_delays:
                exp_delay = carrier_delays[carrier]
                rel = max(0.20, min(1.0, rel - (exp_delay * 0.05)))

            # Normalizations (Transit time: max 20 days, Cost: max $5,000)
            norm_transit = min(1.0, transit_days / 20.0)
            norm_cost = min(1.0, cost / 5000.0)
            hop_factor = 1.0 / hops

            comp_score = (
                0.40 * rel
                + 0.30 * (1.0 - norm_transit)
                + 0.20 * (1.0 - norm_cost)
                + 0.10 * hop_factor
            )

            scored = dict(alt)
            scored["assessed_reliability"] = rel
            scored["composite_rank_score"] = round(comp_score, 4)
            scored_alternates.append(scored)

        scored_alternates.sort(
            key=lambda x: (
                x["composite_rank_score"],
                -(x.get("alt_transit_time_days") if x.get("alt_transit_time_days") is not None else 10.0),
            ),
            reverse=True,
        )
        return scored_alternates

    def analyze(self, context: ScenarioContext) -> StructuredClaim:
        """Executes full transportation analysis workflow and returns StructuredClaim."""
        target_route = context.target_entity_id if context.target_entity_type in ["route", "transport"] else None
        target_carrier = context.target_entity_id if context.target_entity_type == "carrier" else None

        carrier_filter = [target_carrier] if target_carrier else None
        route_filter = [target_route] if target_route else None

        # 1. Fetch shipment history
        shipment_df, shipment_qhash = self.data_access.get_shipment_delivery_history(
            run_id=context.run_id,
            carrier_ids=carrier_filter,
            route_ids=route_filter,
        )

        # 2. Fetch disruptions
        disruptions, _ = self.data_access.get_transport_disruptions(
            run_id=context.run_id,
            scenario_id=context.scenario_id,
        )
        if context.disruption_type:
            ctx_disr = {
                "disruption_type": context.disruption_type,
                "target_entity_type": context.target_entity_type or "route",
                "target_entity_id": context.target_entity_id or "route-sea-01",
                "severity": context.severity or 3,
            }
            if not any(d.get("target_entity_id") == ctx_disr["target_entity_id"] for d in disruptions):
                disruptions.append(ctx_disr)

        # 3. Fetch route graph data and alternates
        route_details, route_qhash = self.data_access.get_route_graph_data(
            origin="sup-01",
            destination="wh-01",
        )

        active_route_id = target_route or "route-sea-01"
        alternates, alt_qhash = self.data_access.get_alternate_routes(
            disrupted_route_id=active_route_id,
            destination="wh-01",
        )

        # Build feature matrix
        X, y, f_names = self.feature_builder.build_features(
            shipment_df=shipment_df,
            disruptions=disruptions,
            route_details=route_details,
        )

        # 4. Run ensemble inference
        ensemble_res = self.ensemble.predict(X)
        mean_delay = float(np.mean(ensemble_res.point_forecast))
        interval_width = float(np.mean(ensemble_res.interval.upper - ensemble_res.interval.lower))

        conf_obj = self.ensemble.confidence_calculator.compute(
            agreement_score=ensemble_res.agreement_score,
            interval_width=interval_width,
            historical_error=0.15,
            max_interval_width=3.0,
        )
        confidence = float(conf_obj.score)

        # Check disruption status
        is_disrupted = (
            context.disruption_type in ["port_congestion", "weather_delay", "canal_blockage", "carrier_strike"]
            or mean_delay >= DELAY_WARNING_DAYS
        )

        # Map carrier delays for ranking
        unique_carriers = list(shipment_df["carrier_id"].unique()) if not shipment_df.empty else ["PacificFreight"]
        carrier_delays = {}
        for idx, c_id in enumerate(unique_carriers):
            if idx < len(ensemble_res.point_forecast):
                carrier_delays[c_id] = float(ensemble_res.point_forecast[idx])
            else:
                carrier_delays[c_id] = 0.5

        ranked_alternates = self.rank_alternate_routes(
            alternates=alternates,
            carrier_delays=carrier_delays,
        )

        # 5. Formulate Claim
        route_label = target_route or target_carrier or "Primary Transport Corridor (route-sea-01)"
        if is_disrupted:
            priority = "HIGH" if mean_delay >= DELAY_CRITICAL_DAYS or (context.severity and context.severity >= 4) else "MEDIUM"
            if ranked_alternates:
                top_alt = ranked_alternates[0]
                alt_id = top_alt.get("alt_route_id", "route-air-02")
                alt_mode = top_alt.get("alt_mode", "air")
                alt_carrier = top_alt.get("alt_carrier", "GlobalAirCargo")
                alt_transit = top_alt.get("alt_transit_time_days", 2.0)
                recommendation = (
                    f"Reroute critical inbound shipments from disrupted corridor {route_label} "
                    f"to alternate {alt_mode} lane ({alt_id} via {alt_carrier}) with estimated {alt_transit:.1f}-day transit."
                )
                reasoning = (
                    f"Transport corridor {route_label} exhibits predicted delay of {mean_delay:.1f} days due to active "
                    f"'{context.disruption_type or 'congestion'}' (severity {context.severity or 3}). "
                    f"Top alternate route {alt_id} ({alt_carrier}, mode: {alt_mode}) provides composite score {top_alt.get('composite_rank_score', 0.0):.2f} "
                    f"with {top_alt.get('assessed_reliability', 0.95):.2f} reliability rating."
                )
            else:
                recommendation = f"Adjust delivery windows and notify downstream production of expected {mean_delay:.1f}-day transit delay."
                reasoning = (
                    f"Transport corridor {route_label} exhibits predicted delay of {mean_delay:.1f} days. "
                    f"No direct alternate corridors found in the route graph."
                )
            impact = "Avoids bottleneck at assembly hub and preserves production schedule commitments."
        else:
            priority = "LOW"
            recommendation = f"Maintain active shipping lanes on {route_label}."
            reasoning = (
                f"Transportation corridors operate within nominal bounds with expected delay of {mean_delay:.1f} days "
                f"across {len(shipment_df)} historical shipment legs. No severe lane disruptions detected."
            )
            impact = "Maintains planned logistics cost and transit schedules."

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

        # Traceable Evidence Items
        builder.add_evidence(
            type="historical_data",
            source="PostgreSQL: shipments table",
            summary=f"Historical shipment performance for {len(unique_carriers)} carrier(s).",
            reference_id=f"shipments:{target_route or 'all'}",
            query_hash=shipment_qhash,
        )
        builder.add_evidence(
            type="graph_query",
            source="Neo4j: (Origin)-[:CONNECTED_TO]->(Destination)",
            summary=f"Topology query for corridor {route_label} returned {len(route_details)} segment(s) and {len(alternates)} alternate(s).",
            reference_id=f"route_graph:{active_route_id}",
            query_hash=route_qhash,
        )
        builder.add_evidence(
            type="model_output",
            source="TransportEnsemble (DelayPredictor + RouteScorer)",
            summary=f"Predicted delay: {mean_delay:.2f} days. Agreement score: {ensemble_res.agreement_score:.3f}.",
            reference_id=f"delay_ensemble:{context.scenario_id or 'default'}",
        )

        return builder.build(confidence_floor=floor)
