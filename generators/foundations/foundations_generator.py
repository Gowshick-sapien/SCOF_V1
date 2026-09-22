"""
Foundations Generator
Handles Tier 0 platform primitives: Reference Dimensions, Dual Calendar, Geography, Parties, and Holidays.
"""

import os
import pandas as pd
import numpy as np
from datetime import date, timedelta
from generators.base_generator import BaseGenerator

class FoundationsGenerator(BaseGenerator):
    def execute(self):
        output_dir = os.path.join(self.context.get("datasets_dir", "datasets"), "foundations")
        os.makedirs(output_dir, exist_ok=True)

        if self.node_id == "GEN_T0_REF":
            return self._generate_reference_dimensions(output_dir)
        elif self.node_id == "GEN_T0_TIME":
            return self._generate_dual_calendar(output_dir)
        elif self.node_id == "GEN_T0_GEO":
            return self._generate_geography(output_dir)
        elif self.node_id == "GEN_T0_PARTY":
            return self._generate_parties(output_dir)
        elif self.node_id == "GEN_T0_HOLIDAY":
            return self._generate_holidays(output_dir)
        else:
            raise ValueError(f"Unknown node_id for FoundationsGenerator: {self.node_id}")

    def _generate_reference_dimensions(self, output_dir: str):
        currencies = [
            {"currency_id": "INR", "currency_name": "Indian Rupee", "symbol": "Rs", "decimal_places": 2, "is_active": True},
            {"currency_id": "USD", "currency_name": "US Dollar", "symbol": "$", "decimal_places": 2, "is_active": True},
            {"currency_id": "EUR", "currency_name": "Euro", "symbol": "EUR", "decimal_places": 2, "is_active": True},
            {"currency_id": "GBP", "currency_name": "British Pound", "symbol": "GBP", "decimal_places": 2, "is_active": True}
        ]
        uoms = [
            {"uom_id": "KG", "uom_name": "Kilogram", "uom_category": "WEIGHT", "conversion_factor_to_base": 1.0},
            {"uom_id": "G", "uom_name": "Gram", "uom_category": "WEIGHT", "conversion_factor_to_base": 0.001},
            {"uom_id": "L", "uom_name": "Liter", "uom_category": "VOLUME", "conversion_factor_to_base": 1.0},
            {"uom_id": "ML", "uom_name": "Milliliter", "uom_category": "VOLUME", "conversion_factor_to_base": 0.001},
            {"uom_id": "EA", "uom_name": "Each", "uom_category": "COUNT", "conversion_factor_to_base": 1.0},
            {"uom_id": "BOX", "uom_name": "Box", "uom_category": "COUNT", "conversion_factor_to_base": 10.0},
            {"uom_id": "PALLET", "uom_name": "Pallet", "uom_category": "COUNT", "conversion_factor_to_base": 100.0}
        ]
        payment_terms = [
            {"payment_term_id": "IMMEDIATE", "term_name": "Immediate Payment", "net_days": 0, "discount_days": 0, "discount_percentage": 0.0},
            {"payment_term_id": "NET_30", "term_name": "Net 30 Days", "net_days": 30, "discount_days": 0, "discount_percentage": 0.0},
            {"payment_term_id": "NET_60", "term_name": "Net 60 Days", "net_days": 60, "discount_days": 0, "discount_percentage": 0.0},
            {"payment_term_id": "2_10_NET_30", "term_name": "2% 10 Net 30", "net_days": 30, "discount_days": 10, "discount_percentage": 2.0}
        ]
        incoterms = [
            {"incoterm_id": "FOB", "incoterm_name": "Free On Board", "risk_transfer_point": "Port of Origin", "freight_payer": "BUYER"},
            {"incoterm_id": "CIF", "incoterm_name": "Cost, Insurance and Freight", "risk_transfer_point": "Port of Destination", "freight_payer": "SELLER"},
            {"incoterm_id": "EXW", "incoterm_name": "Ex Works", "risk_transfer_point": "Seller Premises", "freight_payer": "BUYER"},
            {"incoterm_id": "DDP", "incoterm_name": "Delivered Duty Paid", "risk_transfer_point": "Buyer Premises", "freight_payer": "SELLER"}
        ]

        p_curr = os.path.join(output_dir, "currency.csv")
        pd.DataFrame(currencies).to_csv(p_curr, index=False)
        p_uom = os.path.join(output_dir, "unit_of_measure.csv")
        pd.DataFrame(uoms).to_csv(p_uom, index=False)
        p_pt = os.path.join(output_dir, "payment_terms.csv")
        pd.DataFrame(payment_terms).to_csv(p_pt, index=False)
        p_inco = os.path.join(output_dir, "incoterm.csv")
        pd.DataFrame(incoterms).to_csv(p_inco, index=False)

        total_rows = len(currencies) + len(uoms) + len(payment_terms) + len(incoterms)
        return {
            "status": "SUCCESS",
            "row_count": total_rows,
            "checksum": self.compute_file_checksum(p_curr),
            "output_files": [p_curr, p_uom, p_pt, p_inco],
            "metrics": {"currencies": len(currencies), "uoms": len(uoms)}
        }

    def _generate_dual_calendar(self, output_dir: str):
        # 3-year horizon: 2025 to 2027
        start_dt = date(2025, 1, 1)
        end_dt = date(2027, 12, 31)
        
        dates = []
        curr = start_dt
        while curr <= end_dt:
            iso_yr, iso_wk, iso_dow = curr.isocalendar()
            dates.append({
                "date_id": curr.isoformat(),
                "date_key": curr.year * 10000 + curr.month * 100 + curr.day,
                "year_id": curr.year,
                "month_id": curr.year * 100 + curr.month,
                "week_id": iso_yr * 100 + iso_wk,
                "day_of_week": iso_dow,
                "day_name": curr.strftime("%A"),
                "day_of_month": curr.day,
                "day_of_year": curr.timetuple().tm_yday,
                "is_weekend": iso_dow in (6, 7),
                "is_business_day": iso_dow not in (6, 7)
            })
            curr += timedelta(days=1)

        df_dates = pd.DataFrame(dates)
        p_dates = os.path.join(output_dir, "calendar_date.csv")
        df_dates.to_csv(p_dates, index=False)

        # Weeks
        df_weeks = df_dates.groupby("week_id").agg(
            year_id=("year_id", "first"),
            start_date=("date_id", "min"),
            end_date=("date_id", "max")
        ).reset_index()
        df_weeks["week_number"] = df_weeks["week_id"] % 100
        df_weeks["retail_quarter"] = ((df_weeks["week_number"] - 1) // 13) + 1
        df_weeks["retail_quarter"] = df_weeks["retail_quarter"].clip(1, 4)
        p_weeks = os.path.join(output_dir, "week.csv")
        df_weeks.to_csv(p_weeks, index=False)

        # Fiscal periods (April to March)
        fiscal_periods = []
        for yr in [2025, 2026, 2027]:
            fy_id = f"FY{yr}_{yr+1-2000}"
            for p in range(1, 13):
                m = (p + 2) % 12 + 1
                c_yr = yr if p <= 9 else yr + 1
                fiscal_periods.append({
                    "fiscal_period_id": f"{fy_id}_P{p:02d}",
                    "fiscal_year_id": fy_id,
                    "period_number": p,
                    "period_name": f"P{p:02d}",
                    "calendar_year": c_yr,
                    "calendar_month": m
                })
        df_fp = pd.DataFrame(fiscal_periods)
        p_fp = os.path.join(output_dir, "fiscal_period.csv")
        df_fp.to_csv(p_fp, index=False)

        total_rows = len(df_dates) + len(df_weeks) + len(df_fp)
        return {
            "status": "SUCCESS",
            "row_count": total_rows,
            "checksum": self.compute_file_checksum(p_dates),
            "output_files": [p_dates, p_weeks, p_fp],
            "metrics": {"total_days": len(df_dates), "total_weeks": len(df_weeks)}
        }

    def _generate_geography(self, output_dir: str):
        country = [{"country_id": "IND", "country_name": "India", "iso_2_code": "IN", "currency_id": "INR", "phone_country_code": "+91"}]
        zones = [
            {"zone_id": "ZONE_SOUTH", "country_id": "IND", "zone_name": "South Zone", "climate_zone": "TROPICAL_MONSOON"},
            {"zone_id": "ZONE_NORTH", "country_id": "IND", "zone_name": "North Zone", "climate_zone": "HUMID_SUBTROPICAL"},
            {"zone_id": "ZONE_WEST", "country_id": "IND", "zone_name": "West Zone", "climate_zone": "ARID"},
            {"zone_id": "ZONE_EAST", "country_id": "IND", "zone_name": "East Zone", "climate_zone": "HUMID_SUBTROPICAL"}
        ]
        states = [
            {"state_id": "IN-TN", "country_id": "IND", "zone_id": "ZONE_SOUTH", "state_name": "Tamil Nadu", "gst_state_code": "33"},
            {"state_id": "IN-KA", "country_id": "IND", "zone_id": "ZONE_SOUTH", "state_name": "Karnataka", "gst_state_code": "29"},
            {"state_id": "IN-MH", "country_id": "IND", "zone_id": "ZONE_WEST", "state_name": "Maharashtra", "gst_state_code": "27"},
            {"state_id": "IN-TG", "country_id": "IND", "zone_id": "ZONE_SOUTH", "state_name": "Telangana", "gst_state_code": "36"}
        ]
        cities = [
            {"city_id": "CTY_CHENNAI", "district_id": "DIST_CHN", "city_name": "Chennai", "tier": "TIER_1", "population": 8000000},
            {"city_id": "CTY_BLR", "district_id": "DIST_BLR", "city_name": "Bengaluru", "tier": "TIER_1", "population": 12000000},
            {"city_id": "CTY_MUMBAI", "district_id": "DIST_MUM", "city_name": "Mumbai", "tier": "TIER_1", "population": 15000000},
            {"city_id": "CTY_HYD", "district_id": "DIST_HYD", "city_name": "Hyderabad", "tier": "TIER_1", "population": 9000000}
        ]

        p_geo = os.path.join(output_dir, "geography_nodes.csv")
        df_cities = pd.DataFrame(cities)
        df_cities.to_csv(p_geo, index=False)

        total_rows = len(country) + len(zones) + len(states) + len(cities)
        return {
            "status": "SUCCESS",
            "row_count": total_rows,
            "checksum": self.compute_file_checksum(p_geo),
            "output_files": [p_geo],
            "metrics": {"cities": len(cities), "states": len(states)}
        }

    def _generate_parties(self, output_dir: str):
        # Master enterprise parties
        parties = [
            {"party_id": "PTY-ENT-001", "party_code": "PTY-ENT-001", "party_type": "ORGANIZATION", "legal_name": "SCOF Enterprise Corp", "status": "ACTIVE"},
            {"party_id": "PTY-RET-001", "party_code": "PTY-RET-001", "party_type": "ORGANIZATION", "legal_name": "SCOF Retail Operations Ltd", "status": "ACTIVE"},
            {"party_id": "PTY-LOG-001", "party_code": "PTY-LOG-001", "party_type": "ORGANIZATION", "legal_name": "SCOF Logistics & Supply Ltd", "status": "ACTIVE"}
        ]
        
        # Add 200 suppliers and 25 carriers
        for i in range(1, 201):
            parties.append({
                "party_id": f"PTY-SUP-{i:03d}",
                "party_code": f"PTY-SUP-{i:03d}",
                "party_type": "ORGANIZATION",
                "legal_name": f"Enterprise Supplier {i:03d} Ltd",
                "status": "ACTIVE"
            })
        for i in range(1, 26):
            parties.append({
                "party_id": f"PTY-CARR-{i:03d}",
                "party_code": f"PTY-CARR-{i:03d}",
                "party_type": "ORGANIZATION",
                "legal_name": f"Express Freight Carrier {i:03d} Ltd",
                "status": "ACTIVE"
            })

        # Add sample person parties
        parties.append({
            "party_id": "PTY-EMP-001",
            "party_code": "PTY-EMP-001",
            "party_type": "PERSON",
            "legal_name": "Rajesh Kumar",
            "status": "ACTIVE"
        })
        parties.append({
            "party_id": "PTY-CUST-001",
            "party_code": "PTY-CUST-001",
            "party_type": "PERSON",
            "legal_name": "Suresh Patel",
            "status": "ACTIVE"
        })

        df_parties = pd.DataFrame(parties)
        p_party = os.path.join(output_dir, "party_master.csv")
        df_parties.to_csv(p_party, index=False)

        return {
            "status": "SUCCESS",
            "row_count": len(df_parties),
            "checksum": self.compute_file_checksum(p_party),
            "output_files": [p_party],
            "metrics": {"total_parties": len(df_parties)}
        }

    def _generate_holidays(self, output_dir: str):
        holidays = [
            {"holiday_instance_id": "HOL_2026_NEW_YEAR", "date_id": "2026-01-01", "country_id": "IND", "holiday_name": "New Year's Day", "holiday_type": "COMMERCIAL_OBSERVANCE", "is_facility_closed": False},
            {"holiday_instance_id": "HOL_2026_PONGAL", "date_id": "2026-01-14", "country_id": "IND", "holiday_name": "Pongal / Makar Sankranti", "holiday_type": "REGIONAL_RESTRICTED", "is_facility_closed": False},
            {"holiday_instance_id": "HOL_2026_REPUBLIC", "date_id": "2026-01-26", "country_id": "IND", "holiday_name": "Republic Day", "holiday_type": "NATIONAL_GAZETTED", "is_facility_closed": False},
            {"holiday_instance_id": "HOL_2026_HOLI", "date_id": "2026-03-04", "country_id": "IND", "holiday_name": "Holi", "holiday_type": "NATIONAL_GAZETTED", "is_facility_closed": False},
            {"holiday_instance_id": "HOL_2026_INDEPENDENCE", "date_id": "2026-08-15", "country_id": "IND", "holiday_name": "Independence Day", "holiday_type": "NATIONAL_GAZETTED", "is_facility_closed": False},
            {"holiday_instance_id": "HOL_2026_DIWALI", "date_id": "2026-11-08", "country_id": "IND", "holiday_name": "Diwali / Deepavali", "holiday_type": "NATIONAL_GAZETTED", "is_facility_closed": False},
            {"holiday_instance_id": "HOL_2026_CHRISTMAS", "date_id": "2026-12-25", "country_id": "IND", "holiday_name": "Christmas", "holiday_type": "NATIONAL_GAZETTED", "is_facility_closed": False}
        ]
        df_holidays = pd.DataFrame(holidays)
        p_hol = os.path.join(output_dir, "holiday_instance.csv")
        df_holidays.to_csv(p_hol, index=False)

        return {
            "status": "SUCCESS",
            "row_count": len(df_holidays),
            "checksum": self.compute_file_checksum(p_hol),
            "output_files": [p_hol],
            "metrics": {"holidays": len(df_holidays)}
        }
