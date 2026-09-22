"""
Unit and Integration Test Suite for CognitiveTwinService (Phase 5)
------------------------------------------------------------------
Verifies all 5 contractual API operations:
  1. get_farm_to_store_lineage(sku_id, store_id)
  2. evaluate_demand_shock(event_id, zone_id, week_id)
  3. simulate_disruption(asset_id, downtime_hours, scenario_id, baseline_run_id)
  4. audit_three_way_match(po_id)
  5. get_financial_ledger_summary(fiscal_period_id)
"""

import unittest
from services.twin_service import CognitiveTwinService

class TestCognitiveTwinService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = CognitiveTwinService()

    def test_01_farm_to_store_lineage(self):
        result = self.service.get_farm_to_store_lineage("APP-CHI-00001", "STR-001")
        self.assertEqual(result["status"], "LINEAGE_RESOLVED")
        self.assertIsNotNone(result["merchandise_hierarchy"])
        self.assertIsNotNone(result["store_assortment"])
        self.assertIsNotNone(result["network_servicing"])
        self.assertIsNotNone(result["upstream_sourcing"])
        self.assertEqual(result["sku_id"], "APP-CHI-00001")

    def test_02_evaluate_demand_shock(self):
        result = self.service.evaluate_demand_shock("EV001", "ZONE_SOUTH", 202601)
        self.assertEqual(result["status"], "SHOCK_EVALUATED")
        self.assertIsNotNone(result["event_definition"])
        self.assertGreater(len(result["effective_impacts"]), 0)
        for impact in result["effective_impacts"]:
            self.assertIn("effective_lift_multiplier", impact)

    def test_03_simulate_disruption(self):
        result = self.service.simulate_disruption("AST-0001", 24.0)
        self.assertEqual(result["status"], "SIMULATION_COMPLETED")
        self.assertIn("baseline_state", result)
        self.assertIn("intervention_details", result)
        self.assertIn("affected_entities", result)
        self.assertIn("inventory_impact", result)
        self.assertIn("financial_impact", result)
        self.assertIn("total_financial_exposure", result["financial_impact"])

    def test_04_audit_three_way_match(self):
        result = self.service.audit_three_way_match("PO-2026-000001")
        self.assertEqual(result["status"], "AUDIT_COMPLETE")
        self.assertIn(result["overall_match_status"], ["EXACT_MATCH", "VARIANCE"])
        self.assertEqual(result["qty_check"], "PASS")
        self.assertEqual(result["price_variance_check"], "PASS")

    def test_05_financial_ledger_summary(self):
        result = self.service.get_financial_ledger_summary("FY2026_27_P01")
        self.assertEqual(result["status"], "PERIOD_BALANCED")
        self.assertTrue(result["is_double_entry_balanced"])
        self.assertLessEqual(result["equilibrium_difference"], 0.01)
        self.assertGreater(result["total_debits"], 0)
        self.assertGreater(result["total_credits"], 0)

if __name__ == "__main__":
    unittest.main()
