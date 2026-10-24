"""Slab-based bill calculation (units -> amount)."""
import json, os

_PATH = os.path.join(os.path.dirname(__file__), "tariff.json")

def load_tariff():
    with open(_PATH) as f:
        return json.load(f)

def calculate_bill(units, tariff=None):
    tariff = tariff or load_tariff()
    units = max(0.0, float(units))
    remaining, prev, energy, breakdown = units, 0.0, 0.0, []
    for slab in tariff["slabs"]:
        upto = slab["upto"]
        span = (upto - prev) if upto is not None else remaining
        used = min(remaining, span)
        if used > 0:
            cost = used * slab["rate"]
            energy += cost
            breakdown.append({"from": prev, "to": prev + used, "units": round(used, 2),
                              "rate": slab["rate"], "cost": round(cost, 2)})
        remaining -= used
        prev = upto if upto is not None else prev
        if remaining <= 0:
            break
    subtotal = energy + tariff["fixed_charge"]
    tax = subtotal * tariff["tax_percent"] / 100
    return {"units": round(units, 2), "energy_charge": round(energy, 2),
            "fixed_charge": tariff["fixed_charge"], "tax": round(tax, 2),
            "total": round(subtotal + tax, 2), "breakdown": breakdown}
