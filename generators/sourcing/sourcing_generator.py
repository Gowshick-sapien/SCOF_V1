"""
Sourcing Generator
Handles supplier profiles, carrier profiles, employee profiles, supplier-SKU sourcing matrix (99,232 pairings), and commercial contracts.
Reuses validated V2 supplier sourcing assets.
"""

import os
import pandas as pd
import numpy as np
from generators.base_generator import BaseGenerator

class SourcingGenerator(BaseGenerator):
    def execute(self):
        datasets_dir = self.context.get("datasets_dir", "datasets")
        masters_dir = os.path.join(datasets_dir, "masters")
        output_dir = os.path.join(datasets_dir, "sourcing")
        os.makedirs(output_dir, exist_ok=True)

        if self.node_id == "GEN_T1_PROF":
            return self._generate_profiles(output_dir)
        elif self.node_id == "GEN_T2_SSM":
            return self._verify_and_stage_sourcing_matrix(masters_dir, output_dir)
        elif self.node_id == "GEN_T3_CONT":
            return self._generate_commercial_contracts(output_dir)
        else:
            raise ValueError(f"Unknown node_id for SourcingGenerator: {self.node_id}")

    def _generate_profiles(self, output_dir: str):
        # 200 supplier profiles
        suppliers = []
        for i in range(1, 201):
            suppliers.append({
                "supplier_profile_id": f"SUP-PR-{i:03d}",
                "party_id": f"PTY-SUP-{i:03d}",
                "vendor_tier": "TIER_1" if i <= 40 else "TIER_2",
                "payment_term_id": "NET_30" if i % 2 == 0 else "NET_60",
                "default_currency_id": "INR",
                "incoterm_id": "FOB" if i % 2 == 0 else "CIF",
                "status": "ACTIVE"
            })
        
        # 25 carrier profiles
        carriers = []
        for i in range(1, 26):
            carriers.append({
                "carrier_profile_id": f"CARR-PR-{i:03d}",
                "party_id": f"PTY-CARR-{i:03d}",
                "carrier_type": "LINEHAUL" if i <= 10 else "LAST_MILE",
                "payment_term_id": "NET_30",
                "status": "ACTIVE"
            })

        # 300 employee profiles
        employees = []
        for i in range(1, 301):
            employees.append({
                "employee_profile_id": f"EMP-PR-{i:04d}",
                "party_id": f"PTY-EMP-{i:04d}",
                "workforce_role_id": "ROLE_STORE_MGR" if i <= 16 else "ROLE_OPERATOR",
                "assigned_facility_id": f"STR-{((i % 16) + 1):03d}",
                "status": "ACTIVE"
            })

        p_sup = os.path.join(output_dir, "supplier_profiles.csv")
        pd.DataFrame(suppliers).to_csv(p_sup, index=False)

        p_carr = os.path.join(output_dir, "carrier_profiles.csv")
        pd.DataFrame(carriers).to_csv(p_carr, index=False)

        p_emp = os.path.join(output_dir, "employee_profiles.csv")
        pd.DataFrame(employees).to_csv(p_emp, index=False)

        total_rows = len(suppliers) + len(carriers) + len(employees)
        return {
            "status": "SUCCESS",
            "row_count": total_rows,
            "checksum": self.compute_file_checksum(p_sup),
            "output_files": [p_sup, p_carr, p_emp],
            "metrics": {"suppliers": len(suppliers), "carriers": len(carriers), "employees": len(employees)}
        }

    def _verify_and_stage_sourcing_matrix(self, masters_dir: str, output_dir: str):
        # Authoritative V2 Supplier-SKU Map (99,232 pairings)
        p_ssm = os.path.join(masters_dir, "supplier_sku_map.csv")
        if not os.path.exists(p_ssm):
            raise FileNotFoundError(f"Authoritative supplier SKU map not found: {p_ssm}")

        df_ssm = pd.read_csv(p_ssm)
        row_count = len(df_ssm)
        p_out = os.path.join(output_dir, "supplier_sku_map.csv")
        df_ssm.to_csv(p_out, index=False)

        return {
            "status": "SUCCESS",
            "row_count": row_count,
            "checksum": self.compute_file_checksum(p_out),
            "output_files": [p_out],
            "metrics": {"total_sourcing_edges": row_count}
        }

    def _generate_commercial_contracts(self, output_dir: str):
        # 225 commercial vendor and carrier contracts
        contracts = []
        for i in range(1, 201):
            contracts.append({
                "contract_id": f"CONT-SUP-{i:03d}",
                "party_id": f"PTY-SUP-{i:03d}",
                "contract_type": "SUPPLIER_MASTER_AGREEMENT",
                "start_date": "2025-01-01",
                "end_date": "2027-12-31",
                "payment_term_id": "NET_30",
                "status": "ACTIVE"
            })
        for i in range(1, 26):
            contracts.append({
                "contract_id": f"CONT-CARR-{i:03d}",
                "party_id": f"PTY-CARR-{i:03d}",
                "contract_type": "CARRIER_SERVICE_AGREEMENT",
                "start_date": "2025-01-01",
                "end_date": "2027-12-31",
                "payment_term_id": "NET_30",
                "status": "ACTIVE"
            })

        df_cont = pd.DataFrame(contracts)
        p_cont = os.path.join(output_dir, "commercial_contracts.csv")
        df_cont.to_csv(p_cont, index=False)

        return {
            "status": "SUCCESS",
            "row_count": len(df_cont),
            "checksum": self.compute_file_checksum(p_cont),
            "output_files": [p_cont],
            "metrics": {"total_contracts": len(df_cont)}
        }
