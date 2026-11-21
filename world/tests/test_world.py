import unittest
from datetime import date

from autoq_world import WorldConfig, generate_world


def ids(rows, key="id"):
    return {r[key] for r in rows}


class WorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = generate_world(WorldConfig(seed=7))

    def test_same_seed_same_world(self):
        self.assertEqual(generate_world(WorldConfig(seed=7)).to_dict(), self.w.to_dict())

    def test_different_seed_differs(self):
        self.assertNotEqual(generate_world(WorldConfig(seed=8)).to_dict(), self.w.to_dict())

    def test_size_configurable(self):
        small = generate_world(WorldConfig(seed=7, n_suppliers=3, n_pos=20))
        big = generate_world(WorldConfig(seed=7, n_suppliers=12, n_pos=150))
        self.assertEqual(len(small.suppliers), 3)
        self.assertEqual(len(small.purchase_orders), 20)
        self.assertEqual(len(big.purchase_orders), 150)

    def test_default_is_tiny(self):
        total = sum(len(v) for v in self.w.to_dict().values())
        self.assertTrue(100 <= total <= 2000, total)

    def test_all_tables_present(self):
        for t in ["companies", "plants", "departments", "suppliers", "material_families",
                  "materials", "contracts", "fx_rates", "fiscal_calendar", "purchase_orders",
                  "po_lines", "receipts", "invoices", "credit_notes", "payments"]:
            self.assertGreater(len(getattr(self.w, t)), 0, t)

    def test_unique_ids(self):
        for name, rows in self.w.to_dict().items():
            if rows and "id" in rows[0]:
                self.assertEqual(len(rows), len(ids(rows)), name)

    def test_master_data_references(self):
        w = self.w
        self.assertLessEqual({p["company_id"] for p in w.plants}, ids(w.companies))
        self.assertLessEqual({m["family_id"] for m in w.materials}, ids(w.material_families))
        self.assertLessEqual({c["supplier_id"] for c in w.contracts}, ids(w.suppliers))
        self.assertLessEqual({c["material_id"] for c in w.contracts}, ids(w.materials))
        self.assertLessEqual({d["company_id"] for d in w.departments}, ids(w.companies))

    def test_po_references_and_totals(self):
        w = self.w
        po_ids = ids(w.purchase_orders)
        self.assertLessEqual({l["po_id"] for l in w.po_lines}, po_ids)
        self.assertEqual({l["po_id"] for l in w.po_lines}, po_ids)
        for po in w.purchase_orders:
            self.assertIn(po["supplier_id"], ids(w.suppliers))
            self.assertIn(po["plant_id"], ids(w.plants))
            lines = [l for l in w.po_lines if l["po_id"] == po["id"]]
            self.assertEqual(po["total"], sum(l["qty"] * l["unit_price"] for l in lines))
            for l in lines:
                self.assertIn(l["material_id"], ids(w.materials))

    def test_po_prices_follow_contract(self):
        w = self.w
        for po in w.purchase_orders:
            for l in [l for l in w.po_lines if l["po_id"] == po["id"]]:
                cs = [c for c in w.contracts if c["supplier_id"] == po["supplier_id"]
                      and c["material_id"] == l["material_id"]
                      and c["valid_from"] <= po["date"] <= c["valid_to"]]
                self.assertEqual(len(cs), 1)
                self.assertEqual(cs[0]["unit_price"], l["unit_price"])
                self.assertEqual(cs[0]["currency"], po["currency"])

    def test_receipts_reference_pos(self):
        w = self.w
        pos = {p["id"]: p for p in w.purchase_orders}
        lines = {l["id"]: l for l in w.po_lines}
        self.assertGreater(len(w.receipts), 0)
        for r in w.receipts:
            self.assertIn(r["po_id"], pos)
            self.assertEqual(lines[r["po_line_id"]]["po_id"], r["po_id"])
            self.assertGreaterEqual(r["date"], pos[r["po_id"]]["date"])
        for lid, l in lines.items():
            got = sum(r["qty"] for r in w.receipts if r["po_line_id"] == lid)
            self.assertLessEqual(got, l["qty"])

    def test_invoices_consistent_with_receipts(self):
        w = self.w
        pos = {p["id"]: p for p in w.purchase_orders}
        self.assertGreater(len(w.invoices), 0)
        for inv in w.invoices:
            po = pos[inv["po_id"]]
            self.assertEqual(inv["supplier_id"], po["supplier_id"])
            self.assertEqual(inv["currency"], po["currency"])
            self.assertGreaterEqual(inv["date"], min(
                r["date"] for r in w.receipts if r["po_id"] == po["id"]))
            self.assertGreater(inv["amount"], 0)
        # invoiced never exceeds received value per PO
        lines = {l["id"]: l for l in w.po_lines}
        for po in w.purchase_orders:
            rec = sum(r["qty"] * lines[r["po_line_id"]]["unit_price"]
                      for r in w.receipts if r["po_id"] == po["id"])
            inv = sum(i["amount"] for i in w.invoices if i["po_id"] == po["id"])
            self.assertLessEqual(inv, rec)

    def test_credit_notes_and_payments(self):
        w = self.w
        invs = {i["id"]: i for i in w.invoices}
        for cn in w.credit_notes:
            inv = invs[cn["invoice_id"]]
            self.assertGreaterEqual(cn["date"], inv["date"])
            self.assertEqual(cn["currency"], inv["currency"])
        for inv in w.invoices:
            credits = sum(c["amount"] for c in w.credit_notes if c["invoice_id"] == inv["id"])
            self.assertLessEqual(credits, inv["amount"])
            pays = [p for p in w.payments if p["invoice_id"] == inv["id"]]
            self.assertLessEqual(len(pays), 1)
            for p in pays:
                self.assertEqual(p["amount"], inv["amount"] - credits)
                self.assertGreaterEqual(p["date"], inv["date"])
        self.assertGreater(len(w.credit_notes), 0)
        self.assertGreater(len(w.payments), 0)

    def test_fx_and_fiscal_calendar(self):
        w = self.w
        currencies = {s["currency"] for s in w.suppliers} | {c["currency"] for c in w.companies}
        base = w.config["base_currency"]
        for cur in currencies - {base}:
            self.assertGreaterEqual(len([f for f in w.fx_rates if f["currency"] == cur]), 12)
        for f in w.fx_rates:
            self.assertGreater(f["rate_to_base"], 0)
        for fc in w.fiscal_calendar:
            self.assertIn(fc["company_id"], ids(w.companies))
            self.assertLess(fc["start"], fc["end"])
        # every PO date falls in a fiscal period of its plant's company
        plants = {p["id"]: p for p in w.plants}
        for po in w.purchase_orders:
            cid = plants[po["plant_id"]]["company_id"]
            self.assertTrue(any(fc["company_id"] == cid and fc["start"] <= po["date"] <= fc["end"]
                                for fc in w.fiscal_calendar))

    def test_dates_are_iso(self):
        for po in self.w.purchase_orders:
            date.fromisoformat(po["date"])


if __name__ == "__main__":
    unittest.main()
