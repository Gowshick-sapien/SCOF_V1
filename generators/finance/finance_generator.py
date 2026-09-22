"""
Finance Generator
Handles financial ledgers and settlement flows with strict internal DAG sequencing and double-entry equilibrium:
Supplier_Invoice -> Supplier_Invoice_Line -> Three_Way_Match_Record -> Payment -> Payment_Allocation -> Bank/Settlement -> Journal_Entry -> Journal_Line.
"""

import os
import pandas as pd
import numpy as np
from generators.base_generator import BaseGenerator

class FinanceGenerator(BaseGenerator):
    def execute(self):
        datasets_dir = self.context.get("datasets_dir", "datasets")
        output_dir = os.path.join(datasets_dir, "finance")
        os.makedirs(output_dir, exist_ok=True)

        if self.node_id == "GEN_T7_SUPP_INVOICE":
            return self._generate_supplier_invoices(output_dir)
        elif self.node_id == "GEN_T7_CUST_INVOICE":
            return self._generate_customer_invoices(output_dir)
        elif self.node_id == "GEN_T7_THREE_WAY_MATCH":
            return self._generate_three_way_match(output_dir)
        elif self.node_id == "GEN_T7_PAYMENT":
            return self._generate_payments(output_dir)
        elif self.node_id == "GEN_T7_GL_LEDGER":
            return self._generate_general_ledger(output_dir)
        else:
            raise ValueError(f"Unknown node_id for FinanceGenerator: {self.node_id}")

    def _generate_supplier_invoices(self, output_dir: str):
        # 15,000 supplier invoices with 75,000 invoice lines
        n_inv = 15000
        invoices = []
        invoice_lines = []

        for inv_idx in range(1, n_inv + 1):
            inv_id = f"INV-SUP-2026-{inv_idx:06d}"
            po_id = f"PO-2026-{inv_idx:06d}"
            supp_id = f"SUP-PR-{((inv_idx % 200) + 1):03d}"
            n_lines = int(self.rng.integers(3, 8))

            inv_subtotal = 0.0
            for l_idx in range(1, n_lines + 1):
                qty = int(self.rng.integers(50, 500))
                unit_price = float(np.round(self.rng.uniform(10.0, 200.0), 2))
                l_total = np.round(qty * unit_price, 2)
                inv_subtotal += l_total

                invoice_lines.append({
                    "invoice_line_id": f"{inv_id}-L{l_idx:02d}",
                    "invoice_id": inv_id,
                    "po_line_id": f"{po_id}-L{l_idx:02d}",
                    "sku_id": f"SKU-{int(self.rng.integers(1, 49616)):06d}",
                    "invoiced_quantity": qty,
                    "unit_price": unit_price,
                    "line_amount": l_total
                })

            tax_amt = np.round(inv_subtotal * 0.18, 2)
            invoices.append({
                "invoice_id": inv_id,
                "invoice_number": f"SINV-2026-{inv_idx:06d}",
                "invoice_type": "SUPPLIER_INVOICE",
                "supplier_profile_id": supp_id,
                "purchase_order_id": po_id,
                "invoice_date": "2026-06-01",
                "due_date": "2026-07-01",
                "subtotal_amount": np.round(inv_subtotal, 2),
                "tax_amount": tax_amt,
                "total_amount": np.round(inv_subtotal + tax_amt, 2),
                "status": "APPROVED"
            })

        p_inv = os.path.join(output_dir, "supplier_invoices.parquet")
        df_inv = pd.DataFrame(invoices)
        df_inv.to_parquet(p_inv, index=False)

        p_invl = os.path.join(output_dir, "supplier_invoice_lines.parquet")
        df_invl = pd.DataFrame(invoice_lines)
        df_invl.to_parquet(p_invl, index=False)

        total_rows = len(df_inv) + len(df_invl)
        return {
            "status": "SUCCESS",
            "row_count": total_rows,
            "checksum": self.compute_file_checksum(p_inv),
            "output_files": [p_inv, p_invl],
            "metrics": {"supplier_invoices": len(df_inv), "invoice_lines": len(df_invl)}
        }

    def _generate_customer_invoices(self, output_dir: str):
        # 50,000 customer billing invoices corresponding to POS/e-commerce sales
        n_cinv = 50000
        cinvoices = []
        for i in range(1, n_cinv + 1):
            cinv_id = f"INV-CUST-2026-{i:07d}"
            tx_id = f"TX-2026-{i:07d}"
            subtotal = float(np.round(self.rng.uniform(50.0, 1500.0), 2))
            tax = np.round(subtotal * 0.18, 2)
            cinvoices.append({
                "invoice_id": cinv_id,
                "invoice_number": f"CINV-2026-{i:07d}",
                "invoice_type": "CUSTOMER_INVOICE",
                "sales_transaction_id": tx_id,
                "customer_profile_id": f"CUST-{((i % 4000) + 1):04d}",
                "invoice_date": "2026-06-15",
                "due_date": "2026-06-15",
                "subtotal_amount": subtotal,
                "tax_amount": tax,
                "total_amount": np.round(subtotal + tax, 2),
                "status": "PAID"
            })

        p_cinv = os.path.join(output_dir, "customer_invoices.parquet")
        df_cinv = pd.DataFrame(cinvoices)
        df_cinv.to_parquet(p_cinv, index=False)

        return {
            "status": "SUCCESS",
            "row_count": len(df_cinv),
            "checksum": self.compute_file_checksum(p_cinv),
            "output_files": [p_cinv],
            "metrics": {"customer_invoices": len(df_cinv)}
        }

    def _generate_three_way_match(self, output_dir: str):
        # 75,000 three-way match records matching PO Line, Goods Receipt Line, and Invoice Line
        p_invl = os.path.join(output_dir, "supplier_invoice_lines.parquet")
        if not os.path.exists(p_invl):
            raise FileNotFoundError(f"Supplier invoice lines required for 3-way match: {p_invl}")

        df_invl = pd.read_parquet(p_invl)
        matches = []

        for idx, row in df_invl.iterrows():
            inv_line_id = row["invoice_line_id"]
            po_line_id = row["po_line_id"]
            # GRN line matches PO line index
            grn_line_id = po_line_id.replace("PO-", "GRN-")
            invoiced_qty = row["invoiced_quantity"]

            matches.append({
                "match_id": f"TWM-2026-{idx+1:07d}",
                "po_line_id": po_line_id,
                "goods_receipt_line_id": grn_line_id,
                "invoice_line_id": inv_line_id,
                "po_quantity": invoiced_qty,
                "received_quantity": invoiced_qty,
                "invoiced_quantity": invoiced_qty,
                "po_unit_price": row["unit_price"],
                "invoiced_unit_price": row["unit_price"],
                "quantity_variance": 0,
                "price_variance": 0.0,
                "match_status": "MATCHED",
                "verified_at": "2026-06-02 10:00:00"
            })

        p_twm = os.path.join(output_dir, "three_way_match_records.parquet")
        df_twm = pd.DataFrame(matches)
        df_twm.to_parquet(p_twm, index=False)

        return {
            "status": "SUCCESS",
            "row_count": len(df_twm),
            "checksum": self.compute_file_checksum(p_twm),
            "output_files": [p_twm],
            "metrics": {"matched_records": len(df_twm)}
        }

    def _generate_payments(self, output_dir: str):
        # Disbursements for 15,000 supplier invoices + collections for 50,000 customer invoices
        p_sinv = os.path.join(output_dir, "supplier_invoices.parquet")
        p_cinv = os.path.join(output_dir, "customer_invoices.parquet")
        
        df_sinv = pd.read_parquet(p_sinv)
        df_cinv = pd.read_parquet(p_cinv)

        payments = []
        allocations = []

        # 1. Supplier disbursements
        for idx, row in df_sinv.iterrows():
            pay_id = f"PAY-DISB-2026-{idx+1:06d}"
            amt = float(row["total_amount"])
            payments.append({
                "payment_id": pay_id,
                "payment_type": "DISBURSEMENT",
                "party_id": row["supplier_profile_id"],
                "payment_date": "2026-06-28",
                "payment_amount": amt,
                "currency_id": "INR",
                "payment_status": "SETTLED"
            })
            allocations.append({
                "allocation_id": f"ALOC-2026-{idx+1:06d}",
                "payment_id": pay_id,
                "invoice_id": row["invoice_id"],
                "allocated_amount": amt,
                "discount_applied": 0.0
            })

        # 2. Customer collections
        for idx, row in df_cinv.iterrows():
            pay_id = f"PAY-COLL-2026-{idx+1:07d}"
            amt = float(row["total_amount"])
            payments.append({
                "payment_id": pay_id,
                "payment_type": "COLLECTION",
                "party_id": row["customer_profile_id"],
                "payment_date": row["invoice_date"],
                "payment_amount": amt,
                "currency_id": "INR",
                "payment_status": "SETTLED"
            })
            allocations.append({
                "allocation_id": f"ALOC-CUST-2026-{idx+1:07d}",
                "payment_id": pay_id,
                "invoice_id": row["invoice_id"],
                "allocated_amount": amt,
                "discount_applied": 0.0
            })

        p_pay = os.path.join(output_dir, "payments.parquet")
        df_pay = pd.DataFrame(payments)
        df_pay.to_parquet(p_pay, index=False)

        p_aloc = os.path.join(output_dir, "payment_allocations.parquet")
        df_aloc = pd.DataFrame(allocations)
        df_aloc.to_parquet(p_aloc, index=False)

        total_rows = len(df_pay) + len(df_aloc)
        return {
            "status": "SUCCESS",
            "row_count": total_rows,
            "checksum": self.compute_file_checksum(p_pay),
            "output_files": [p_pay, p_aloc],
            "metrics": {"payments": len(df_pay), "allocations": len(df_aloc)}
        }

    def _generate_general_ledger(self, output_dir: str):
        # Double-entry General Ledger postings with exact equilibrium: SUM(Debits) == SUM(Credits)
        coa = [{"chart_of_accounts_id": "COA-STANDARD", "coa_name": "SCOF Standard Enterprise Chart of Accounts", "currency_id": "INR"}]
        gl_accounts = [
            {"gl_account_id": "1010", "account_name": "Cash and Cash Equivalents", "account_type": "ASSET", "normal_balance": "DEBIT"},
            {"gl_account_id": "1110", "account_name": "Accounts Receivable", "account_type": "ASSET", "normal_balance": "DEBIT"},
            {"gl_account_id": "1210", "account_name": "Inventory Asset", "account_type": "ASSET", "normal_balance": "DEBIT"},
            {"gl_account_id": "2010", "account_name": "Accounts Payable", "account_type": "LIABILITY", "normal_balance": "CREDIT"},
            {"gl_account_id": "4010", "account_name": "Merchandise Sales Revenue", "account_type": "REVENUE", "normal_balance": "CREDIT"},
            {"gl_account_id": "5010", "account_name": "Cost of Goods Sold", "account_type": "EXPENSE", "normal_balance": "DEBIT"}
        ]

        # Generate 25,000 balanced journal entries
        n_je = 25000
        journal_entries = []
        journal_lines = []

        for i in range(1, n_je + 1):
            je_id = f"JE-2026-{i:06d}"
            amt = float(np.round(self.rng.uniform(100.0, 50000.0), 2))
            journal_entries.append({
                "journal_entry_id": je_id,
                "entry_number": f"GEN-2026-{i:06d}",
                "posting_date": "2026-06-15",
                "fiscal_period_id": "FY2026_27_P03",
                "total_debit_amount": amt,
                "total_credit_amount": amt,
                "is_posted": True
            })

            # Balanced pair (debit Inventory, credit Accounts Payable)
            journal_lines.append({
                "journal_line_id": f"{je_id}-L01",
                "journal_entry_id": je_id,
                "gl_account_id": "1210",
                "debit_amount": amt,
                "credit_amount": 0.0,
                "line_description": "Inventory acquisition"
            })
            journal_lines.append({
                "journal_line_id": f"{je_id}-L02",
                "journal_entry_id": je_id,
                "gl_account_id": "2010",
                "debit_amount": 0.0,
                "credit_amount": amt,
                "line_description": "Supplier payable recognition"
            })

        p_coa = os.path.join(output_dir, "chart_of_accounts.csv")
        pd.DataFrame(coa).to_csv(p_coa, index=False)

        p_gl = os.path.join(output_dir, "gl_accounts.csv")
        pd.DataFrame(gl_accounts).to_csv(p_gl, index=False)

        p_je = os.path.join(output_dir, "journal_entries.parquet")
        df_je = pd.DataFrame(journal_entries)
        df_je.to_parquet(p_je, index=False)

        p_jl = os.path.join(output_dir, "journal_lines.parquet")
        df_jl = pd.DataFrame(journal_lines)
        df_jl.to_parquet(p_jl, index=False)

        total_rows = len(coa) + len(gl_accounts) + len(df_je) + len(df_jl)
        return {
            "status": "SUCCESS",
            "row_count": total_rows,
            "checksum": self.compute_file_checksum(p_je),
            "output_files": [p_coa, p_gl, p_je, p_jl],
            "metrics": {
                "journal_entries": len(df_je),
                "journal_lines": len(df_jl),
                "total_debits": float(df_jl["debit_amount"].sum()),
                "total_credits": float(df_jl["credit_amount"].sum())
            }
        }
