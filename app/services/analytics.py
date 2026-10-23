"""Operations intelligence service — models the correlation between meteorological conditions,

grid stability, and high-performance digital asset/mining infrastructure.
"""

from __future__ import annotations

from app.schemas.dashboard import OperationalImpact


def assess_operational_impact(
    temperature_celsius: float,
    wind_speed_kmh: float,
) -> OperationalImpact:
    """Evaluate thermodynamic cooling demand, regional grid strain risk, and curtailment advisory.

    Domain Rules:
    - Heatwave (>35°C): High HVAC load; regional grid strained by AC peak; high curtailment risk.
    - Freezing (<-5°C): High municipal heating demand on grid; free-air cooling enabled, but grid risk is high.
    - Warm (25°C-35°C): Moderate HVAC cooling overhead; standard grid monitoring.
    - Mild/Optimal (0°C-25°C): Free or low-cost air cooling; minimal grid stress.
    """
    if temperature_celsius > 35.0:
        return OperationalImpact(
            cooling_demand="high",
            grid_stress_risk="high",
            curtailment_advisory=(
                "Critical ambient heat and grid strain. Activate facility cooling economizers "
                "and monitor spot power prices for load curtailment."
            ),
        )

    if temperature_celsius < -5.0:
        return OperationalImpact(
            cooling_demand="low",
            grid_stress_risk="high",
            curtailment_advisory=(
                "Severe cold front creates municipal heating strain on the local grid. "
                "Free-air cooling available, but monitor regional capacity reserves."
            ),
        )

    if temperature_celsius > 25.0:
        return OperationalImpact(
            cooling_demand="moderate",
            grid_stress_risk="moderate",
            curtailment_advisory=(
                "Moderate thermal load. Standard facility HVAC cooling operating "
                "within baseline parameters."
            ),
        )

    return OperationalImpact(
        cooling_demand="low",
        grid_stress_risk="low",
        curtailment_advisory=(
            "Optimal thermodynamic efficiency. Natural convective cooling effective; "
            "normal compute operations recommended."
        ),
    )
