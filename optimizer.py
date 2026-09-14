from __future__ import annotations

from typing import Any
import numpy as np
from scipy.optimize import linprog


def optimize_production(crops: list[dict[str, Any]], hectares: float, water: float,
                         budget: float, labor: float, limits: dict[int, float]) -> dict[str, Any]:
    if not crops:
        return {"success": False, "message": "No hay cultivos disponibles."}
    if any(float(x) < 0 for x in (hectares, water, budget, labor)):
        return {"success": False, "message": "Los recursos no pueden ser negativos."}

    profits = np.array([float(c["price"]) * float(c["yield_per_ha"]) - float(c["cost"]) for c in crops])
    water_use = np.array([float(c["water"]) for c in crops])
    costs = np.array([float(c["cost"]) for c in crops])
    labor_use = np.array([float(c["labor"]) for c in crops])
    A_ub = np.vstack([np.ones(len(crops)), water_use, costs, labor_use])
    b_ub = np.array([hectares, water, budget, labor], dtype=float)
    bounds = [(0.0, max(0.0, float(limits.get(int(c["id"]), c["max_ha"])))) for c in crops]

    result = linprog(-profits, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if not result.success:
        return {"success": False, "message": "No se encontró una solución factible. Revisa los recursos y límites."}

    x = np.maximum(result.x, 0.0)
    rows = []
    for crop, ha in zip(crops, x):
        ha = float(ha)
        profit_ha = float(crop["price"]) * float(crop["yield_per_ha"]) - float(crop["cost"])
        rows.append({"name": crop["name"], "hectares": ha, "profit": ha * profit_ha,
                     "water": ha * float(crop["water"]), "cost": ha * float(crop["cost"]),
                     "labor": ha * float(crop["labor"])})

    land_used = float(x.sum())
    water_used = float(np.dot(x, water_use))
    cost_used = float(np.dot(x, costs))
    labor_used = float(np.dot(x, labor_use))
    profit = float(np.dot(x, profits))
    return {"success": True, "message": "Solución óptima encontrada.", "profit": profit,
            "land_used": land_used, "water_used": water_used, "cost_used": cost_used,
            "labor_used": labor_used, "land_left": max(0.0, hectares-land_used),
            "water_left": max(0.0, water-water_used), "budget_left": max(0.0, budget-cost_used),
            "labor_left": max(0.0, labor-labor_used), "crops": rows}
