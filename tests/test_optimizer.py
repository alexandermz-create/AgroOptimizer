from database import DEFAULT_CROPS
from optimizer import optimize_production


def make_crops():
    fields = ["id", "name", "category", "price", "yield_per_ha", "cost", "labor", "water", "light", "min_temp", "max_temp", "max_ha", "active"]
    return [dict(zip(fields, [i + 1, *row])) for i, row in enumerate(DEFAULT_CROPS)]


def test_optimizer_returns_feasible_solution():
    crops = make_crops()
    limits = {c["id"]: 10.0 for c in crops}
    result = optimize_production(crops, 10, 50000, 50000, 300, limits)
    assert result["success"] is True
    assert result["land_used"] <= 10.000001
    assert result["water_used"] <= 50000.000001
    assert result["cost_used"] <= 50000.000001
    assert result["labor_used"] <= 300.000001
    assert result["profit"] >= 0
