from __future__ import annotations
from dataclasses import dataclass
from random import uniform

@dataclass(frozen=True)
class SensorReading:
    temperature: float
    light: float
    pressure: float
    proximity: float
    humidity: float

def simulate_sensors(temperature: float, light: float, pressure: float, proximity: float, humidity: float) -> SensorReading:
    return SensorReading(float(temperature), float(light), float(pressure), float(proximity), float(humidity))

def random_sensors() -> SensorReading:
    return SensorReading(round(uniform(15,40),1), round(uniform(20,100),1), round(uniform(.5,3.5),2), round(uniform(5,200),1), round(uniform(20,90),1))
