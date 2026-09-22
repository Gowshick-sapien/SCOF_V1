"""
Governance Generator
Handles Tier 1 enterprise governance structure: Enterprise, Legal Entities, Business Units, Divisions, Departments, and Cost/Profit Centers.
"""

import os
import pandas as pd
from generators.base_generator import BaseGenerator

class GovernanceGenerator(BaseGenerator):
    def execute(self):
        output_dir = os.path.join(self.context.get("datasets_dir", "datasets"), "governance")
        os.makedirs(output_dir, exist_ok=True)

        enterprise = [{"enterprise_id": "ENT-001", "party_id": "PTY-ENT-001", "corporate_name": "SCOF Enterprise Corp", "headquarters_country_id": "IND"}]
        legal_entities = [
            {"legal_entity_id": "LENT-001", "enterprise_id": "ENT-001", "registered_name": "SCOF Retail Operations Ltd", "country_id": "IND", "cin": "U52100TN2020PLC000001"},
            {"legal_entity_id": "LENT-002", "enterprise_id": "ENT-001", "registered_name": "SCOF Supply Chain Logistics Ltd", "country_id": "IND", "cin": "U63090TN2020PLC000002"}
        ]
        business_units = [
            {"business_unit_id": "BU-RETAIL", "legal_entity_id": "LENT-001", "bu_name": "Retail Supermarkets BU", "currency_id": "INR"},
            {"business_unit_id": "BU-LOGISTICS", "legal_entity_id": "LENT-002", "bu_name": "Logistics & Fulfillment BU", "currency_id": "INR"}
        ]
        divisions = [
            {"division_id": "DIV-FOOD-GROCERY", "business_unit_id": "BU-RETAIL", "division_name": "Food & Staples", "segment_type": "CORE"},
            {"division_id": "DIV-FRESH", "business_unit_id": "BU-RETAIL", "division_name": "Fresh Foods & Dairy", "segment_type": "PERISHABLE"},
            {"division_id": "DIV-GENERAL-MDSE", "business_unit_id": "BU-RETAIL", "division_name": "General Merchandise", "segment_type": "NON_FOOD"},
            {"division_id": "DIV-TRANSPORT", "business_unit_id": "BU-LOGISTICS", "division_name": "Fleet & Linehaul", "segment_type": "LOGISTICS"}
        ]
        departments = [
            {"org_department_id": "DEPT-MERCH", "division_id": "DIV-FOOD-GROCERY", "department_name": "Merchandising & Category Management"},
            {"org_department_id": "DEPT-PROCURE", "division_id": "DIV-FOOD-GROCERY", "department_name": "Procurement & Sourcing"},
            {"org_department_id": "DEPT-STORE-OPS", "division_id": "DIV-FOOD-GROCERY", "department_name": "Retail Store Operations"},
            {"org_department_id": "DEPT-DC-OPS", "division_id": "DIV-TRANSPORT", "department_name": "Distribution Center Operations"},
            {"org_department_id": "DEPT-FINANCE", "division_id": "DIV-FOOD-GROCERY", "department_name": "Finance & Controllership"}
        ]
        cost_centers = [
            {"cost_center_id": f"CC-{i:03d}", "org_department_id": departments[i % len(departments)]["org_department_id"], "cost_center_name": f"Cost Center {i:03d}", "budget_currency_id": "INR"}
            for i in range(1, 11)
        ]
        profit_centers = [
            {"profit_center_id": f"PC-{i:03d}", "division_id": divisions[i % len(divisions)]["division_id"], "profit_center_name": f"Profit Center {i:03d}", "target_margin_pct": 22.5}
            for i in range(1, 7)
        ]

        p_ent = os.path.join(output_dir, "enterprise_structure.csv")
        pd.DataFrame(enterprise).to_csv(p_ent, index=False)
        p_lent = os.path.join(output_dir, "legal_entities.csv")
        pd.DataFrame(legal_entities).to_csv(p_lent, index=False)
        p_bu = os.path.join(output_dir, "business_units.csv")
        pd.DataFrame(business_units).to_csv(p_bu, index=False)

        total_rows = len(enterprise) + len(legal_entities) + len(business_units) + len(divisions) + len(departments) + len(cost_centers) + len(profit_centers)
        return {
            "status": "SUCCESS",
            "row_count": total_rows,
            "checksum": self.compute_file_checksum(p_ent),
            "output_files": [p_ent, p_lent, p_bu],
            "metrics": {"enterprise_nodes": total_rows}
        }
