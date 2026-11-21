"""Seeded generator of a tiny hidden procure-to-pay World Model.

Pure standard library; deterministic for a given WorldConfig. Money amounts are
integer minor units (cents) in the document currency. Dates are ISO strings.
Drivers and the Answer Key are NOT planted here (next ticket).
"""
import random
from dataclasses import dataclass, field, fields
from datetime import date, timedelta
from typing import Dict, List

Row = Dict[str, object]

TABLES = ["companies", "plants", "departments", "suppliers", "material_families",
          "materials", "contracts", "fx_rates", "fiscal_calendar", "purchase_orders",
          "po_lines", "receipts", "invoices", "credit_notes", "payments"]


@dataclass(frozen=True)
class WorldConfig:
    seed: int = 1
    n_companies: int = 2
    plants_per_company: int = 2
    n_suppliers: int = 8
    n_families: int = 4
    n_materials: int = 12
    n_pos: int = 60
    base_currency: str = "EUR"
    start_year: int = 2024
    n_years: int = 2
    currencies: tuple = ("EUR", "USD", "GBP")


@dataclass
class World:
    config: Dict[str, object]
    companies: List[Row] = field(default_factory=list)
    plants: List[Row] = field(default_factory=list)
    departments: List[Row] = field(default_factory=list)
    suppliers: List[Row] = field(default_factory=list)
    material_families: List[Row] = field(default_factory=list)
    materials: List[Row] = field(default_factory=list)
    contracts: List[Row] = field(default_factory=list)
    fx_rates: List[Row] = field(default_factory=list)
    fiscal_calendar: List[Row] = field(default_factory=list)
    purchase_orders: List[Row] = field(default_factory=list)
    po_lines: List[Row] = field(default_factory=list)
    receipts: List[Row] = field(default_factory=list)
    invoices: List[Row] = field(default_factory=list)
    credit_notes: List[Row] = field(default_factory=list)
    payments: List[Row] = field(default_factory=list)

    def to_dict(self) -> Dict[str, List[Row]]:
        return {t: getattr(self, t) for t in TABLES}


def _iso(d: date) -> str:
    return d.isoformat()


def generate_world(cfg: WorldConfig = WorldConfig()) -> World:
    rng = random.Random(cfg.seed)
    cfg_dict = {f.name: getattr(cfg, f.name) for f in fields(cfg)}
    w = World(config=cfg_dict)
    start = date(cfg.start_year, 1, 1)
    end = date(cfg.start_year + cfg.n_years - 1, 12, 31)
    non_base = [c for c in cfg.currencies if c != cfg.base_currency]

    # Companies, plants, departments, fiscal calendars (company 2+ has April-March year)
    for ci in range(cfg.n_companies):
        cid = f"C{ci + 1}"
        w.companies.append({"id": cid, "name": f"Company {ci + 1}",
                            "currency": cfg.base_currency,
                            "fiscal_year_start_month": 1 if ci % 2 == 0 else 4})
        for pi in range(cfg.plants_per_company):
            w.plants.append({"id": f"{cid}-P{pi + 1}", "company_id": cid,
                             "name": f"Plant {ci + 1}.{pi + 1}"})
        for dn in ("Procurement", "Finance", "Plants"):
            w.departments.append({"id": f"{cid}-{dn[:3].upper()}", "company_id": cid, "name": dn})
        m = 1 if ci % 2 == 0 else 4
        for y in range(cfg.start_year - 1, cfg.start_year + cfg.n_years + 1):
            for q in range(12):
                mm = (m - 1 + q) % 12 + 1
                yy = y + (m - 1 + q) // 12
                s = date(yy, mm, 1)
                e = (date(yy + (mm == 12), mm % 12 + 1, 1)) - timedelta(days=1)
                label_year = y if m == 1 else y + 1
                w.fiscal_calendar.append({
                    "id": f"{cid}-FY{label_year}-{q + 1:02d}", "company_id": cid,
                    "fiscal_year": label_year, "period": q + 1,
                    "start": _iso(s), "end": _iso(e)})

    # FX: monthly random walk, rate_to_base
    month_starts = []
    d = date(start.year - 1, 1, 1)
    while d <= end + timedelta(days=60):
        month_starts.append(d)
        d = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    for cur in non_base:
        rate = rng.uniform(0.8, 1.2)
        for ms in month_starts:
            rate = max(0.3, rate * (1 + rng.uniform(-0.02, 0.02)))
            w.fx_rates.append({"id": f"FX-{cur}-{ms:%Y%m}", "currency": cur,
                               "month": _iso(ms), "rate_to_base": round(rate, 5)})

    # Families, materials
    for fi in range(cfg.n_families):
        w.material_families.append({"id": f"F{fi + 1}", "name": f"Family {fi + 1}"})
    for mi in range(cfg.n_materials):
        w.materials.append({"id": f"M{mi + 1}", "name": f"Material {mi + 1}",
                            "family_id": f"F{mi % cfg.n_families + 1}",
                            "uom": rng.choice(["EA", "KG", "L"])})

    # Suppliers
    for si in range(cfg.n_suppliers):
        w.suppliers.append({"id": f"S{si + 1}", "name": f"Supplier {si + 1}",
                            "currency": rng.choice(cfg.currencies),
                            "region": rng.choice(["EU", "NA", "APAC"]),
                            "payment_terms_days": rng.choice([30, 45, 60]),
                            "certified": rng.random() < 0.6})

    # Contracts: each supplier supplies a few materials; two consecutive yearly price periods
    for s in w.suppliers:
        mats = rng.sample(w.materials, k=min(len(w.materials), rng.randint(2, 4)))
        for m in mats:
            base = rng.randint(200, 20000)
            for yi in range(cfg.n_years):
                y = cfg.start_year + yi
                base = int(base * rng.uniform(1.0, 1.08))
                w.contracts.append({
                    "id": f"K{len(w.contracts) + 1}", "supplier_id": s["id"],
                    "material_id": m["id"], "currency": s["currency"], "unit_price": base,
                    "valid_from": _iso(date(y, 1, 1)), "valid_to": _iso(date(y, 12, 31))})

    # POs -> lines -> receipts -> invoices -> credit notes -> payments
    span = (end - start).days - 120
    for pi in range(cfg.n_pos):
        s = rng.choice(w.suppliers)
        po_date = start + timedelta(days=rng.randint(0, span))
        plant = rng.choice(w.plants)
        po_id = f"PO{pi + 1}"
        avail = [c for c in w.contracts if c["supplier_id"] == s["id"]
                 and c["valid_from"] <= _iso(po_date) <= c["valid_to"]]
        picks = rng.sample(avail, k=min(len(avail), rng.randint(1, 3)))
        total = 0
        lines = []
        for c in picks:
            qty = rng.randint(1, 50)
            line = {"id": f"{po_id}-{len(lines) + 1}", "po_id": po_id,
                    "material_id": c["material_id"], "qty": qty, "unit_price": c["unit_price"]}
            lines.append(line)
            total += qty * c["unit_price"]
        w.po_lines.extend(lines)
        w.purchase_orders.append({"id": po_id, "supplier_id": s["id"], "plant_id": plant["id"],
                                  "currency": s["currency"], "date": _iso(po_date),
                                  "total": total})
        # receipts (some lines partially received, some unreceived)
        rec_date = po_date + timedelta(days=rng.randint(5, 30))
        received_value = 0
        for line in lines:
            if rng.random() < 0.1:
                continue
            qty = line["qty"] if rng.random() < 0.8 else max(1, line["qty"] // 2)
            w.receipts.append({"id": f"R{len(w.receipts) + 1}", "po_id": po_id,
                               "po_line_id": line["id"], "qty": qty, "date": _iso(rec_date)})
            received_value += qty * line["unit_price"]
        if received_value == 0:
            continue
        # invoice for the received value
        inv_date = rec_date + timedelta(days=rng.randint(1, 15))
        inv_id = f"I{len(w.invoices) + 1}"
        w.invoices.append({"id": inv_id, "po_id": po_id, "supplier_id": s["id"],
                           "currency": s["currency"], "date": _iso(inv_date),
                           "amount": received_value})
        credit = 0
        if rng.random() < 0.15:
            credit = int(received_value * rng.uniform(0.02, 0.2))
            w.credit_notes.append({"id": f"CN{len(w.credit_notes) + 1}", "invoice_id": inv_id,
                                   "currency": s["currency"],
                                   "date": _iso(inv_date + timedelta(days=rng.randint(1, 30))),
                                   "amount": credit})
        if rng.random() < 0.9:
            pay_date = inv_date + timedelta(
                days=max(1, s["payment_terms_days"] + rng.randint(-10, 20)))
            w.payments.append({"id": f"PAY{len(w.payments) + 1}", "invoice_id": inv_id,
                               "currency": s["currency"], "date": _iso(pay_date),
                               "amount": received_value - credit})
    return w
