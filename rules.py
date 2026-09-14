from __future__ import annotations
from typing import Any

def evaluate_rules(reading: Any) -> list[dict[str,str]]:
    alerts=[]
    if reading.temperature > 35 and reading.humidity < 40:
        alerts.append({"level":"Alta","message":"Posible estrés hídrico: temperatura alta y humedad baja.","action":"Priorizar revisión del riego."})
    elif reading.temperature > 35:
        alerts.append({"level":"Media","message":"Temperatura elevada.","action":"Supervisar riego y ventilación."})
    if reading.light < 30:
        alerts.append({"level":"Media","message":"Iluminación baja.","action":"Revisar exposición solar o iluminación."})
    if reading.pressure < 1.0:
        alerts.append({"level":"Alta","message":"Presión de riego baja.","action":"Revisar bomba, tubería y posibles fugas."})
    if reading.proximity < 20:
        alerts.append({"level":"Baja","message":"Objeto cercano detectado.","action":"Revisar el área de trabajo."})
    if not alerts:
        alerts.append({"level":"Normal","message":"Lecturas dentro de los rangos de simulación.","action":"Continuar con el monitoreo."})
    return alerts

def climate_factor(reading: Any) -> float:
    factor=1.0
    if reading.temperature > 35: factor*=.85
    if reading.humidity < 40: factor*=.90
    if reading.light < 30: factor*=.95
    return factor
