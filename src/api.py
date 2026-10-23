
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .diagnostics import analyse_coolant_temperature
from .hypotheses import rank_hypotheses
from .validation import validate_vehicle_trace


app = FastAPI(
    title="TorqueTrace API",
    description=(
        "Vehicle sensor trace analysis and "
        "diagnostic decision support."
    ),
    version="0.1.0",
)


class DiagnosisRequest(BaseModel):
    readings: list[dict[str, float]]


@app.get("/")
def home():
    return {
        "project": "TorqueTrace",
        "status": "running",
        "message": "Vehicle diagnostic API is ready.",
    }


@app.post("/diagnose")
def diagnose(request: DiagnosisRequest):
    readings = request.readings

    try:
        validate_vehicle_trace(
            readings,
            required_fields=(
                "time_seconds",
                "coolant_temp_c",
                "rpm",
                "engine_load_pct",
            ),
        )

        temperature_analysis = analyse_coolant_temperature(
            readings
        )

        hypothesis_analysis = rank_hypotheses(readings)

        return {
            "temperature_analysis": temperature_analysis,
            "diagnostic_analysis": hypothesis_analysis,
            "disclaimer": (
                "These results are preliminary screening findings, "
                "not confirmed vehicle faults. Verify findings "
                "with appropriate tests."
            ),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error
