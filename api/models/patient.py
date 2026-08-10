"""
api/models/patient.py — Pydantic v2 input model.
Authoritative API input contract.
frontend/src/lib/types.ts BiomarkerInput must mirror this.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class BiomarkerInput(BaseModel):
    LDL_mgdl:   float | None = Field(None, ge=0, le=500)
    HDL_mgdl:   float | None = Field(None, ge=0, le=200)
    TG_mgdl:    float | None = Field(None, ge=0, le=5000)
    TC_mgdl:    float | None = Field(None, ge=0, le=700)
    FPG_mgdl:   float | None = Field(None, ge=0, le=1000)
    # Fasting status for FPG_mgdl. FPG thresholds (docs/CLINICAL_LOGIC_APPENDIX.md)
    # require >= 8 hours fasting (NHANES PHAFSTHR >= 8) and explicitly say "do not
    # classify non-fasting values" — that requirement was documented but not
    # enforced in code until this field existed. "unknown" (including omitted,
    # the default) is treated the same as "not_fasting": FPG is only classified
    # against fasting-glucose categories when fasting_status == "confirmed".
    fasting_status: str | None = Field(None, pattern=r"^(confirmed|not_fasting|unknown)$")
    fasting_hours:  float | None = Field(None, ge=0, le=72)
    HbA1c_pct:  float | None = Field(None, ge=0, le=20)
    SBP_mmhg:   float | None = Field(None, ge=0, le=300)
    DBP_mmhg:   float | None = Field(None, ge=0, le=200)
    BMI_kgm2:   float | None = Field(None, ge=10, le=80)
    # Advanced lipid risk-enhancing markers (optional; classification-only, not
    # cohort-benchmarked). See clinical/thresholds.classify_risk_enhancing_markers.
    ApoB_mgdl:  float | None = Field(None, ge=0, le=300)
    Lpa_mgdl:   float | None = Field(None, ge=0, le=500)
    age_yr:     int   | None = Field(None, ge=18, le=120)
    sex:        str   | None = Field(None, pattern=r"^[MF]$")
    south_asian:bool  | None = Field(None)
    bp_med:   bool = Field(False)
    chol_med: bool = Field(False)
    insulin:  bool = Field(False)
    dm_pills: bool = Field(False)

    model_config = {"json_schema_extra": {"example": {
        "LDL_mgdl": 95, "HDL_mgdl": 62, "TG_mgdl": 120, "TC_mgdl": 185,
        "FPG_mgdl": 88, "fasting_status": "confirmed", "fasting_hours": 10,
        "HbA1c_pct": 5.2, "SBP_mmhg": 115, "DBP_mmhg": 74,
        "BMI_kgm2": 22.1, "age_yr": 45, "sex": "M", "south_asian": True,
        "bp_med": False, "chol_med": False, "insulin": False, "dm_pills": False,
    }}}
