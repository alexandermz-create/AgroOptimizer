# 🌱 AgroOptimizer

Sistema académico de optimización y monitoreo agrícola.

## Objetivo

Encontrar una distribución de cultivos que maximice la ganancia respetando terreno, agua, presupuesto, mano de obra y límites por cultivo, integrando Programación Lineal, Programación Lógica y Funcional y Sistemas Programables.

## Funcionalidades

- Dashboard agrícola.
- CRUD de cultivos con SQLite.
- Precio, rendimiento, costos, agua y trabajo.
- Optimización con `scipy.optimize.linprog`.
- Sensores simulados: temperatura, óptico/luz, presión, proximidad y humedad.
- Motor de reglas SI/ENTONCES.
- Escenarios de sequía y presupuesto limitado.
- Gráficas interactivas con Plotly.

## Estructura

```text
AgroOptimizer/
├── app.py
├── database.py
├── optimizer.py
├── sensors.py
├── rules.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── config.toml
```

La base `agrooptimizer.db` se crea automáticamente y no se versiona.

## Ejecutar en Windows

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Modelo matemático

Para cada cultivo `i`, `x_i` representa hectáreas asignadas.

```text
Max Z = Σ (precio_i × rendimiento_i - costo_i) × x_i

Σ x_i ≤ terreno disponible
Σ agua_i × x_i ≤ agua disponible
Σ costo_i × x_i ≤ presupuesto
Σ trabajo_i × x_i ≤ mano de obra
0 ≤ x_i ≤ máximo_i
```

## Reglas lógicas

```text
SI temperatura > 35 Y humedad < 40 → alertar estrés hídrico
SI presión < 1.0 → revisar sistema de riego
SI luz < 30 → revisar iluminación
SI proximidad < 20 → alertar objeto cercano
```

Los sensores son simulados por software en esta versión. Posteriormente pueden sustituirse por lecturas de ESP32/Arduino.

## Aviso académico

Los valores iniciales son demostrativos. Para decisiones reales deben sustituirse por datos locales confiables de precios, rendimientos, costos, agua, clima y condiciones agronómicas.
