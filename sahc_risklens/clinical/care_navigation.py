"""
sahc_risklens/clinical/care_navigation.py

Care-navigation prompts: low-cost, on-brand "next steps" that route the patient
toward people and programs — NOT clinical advice. Two items, both static template
text (no LLM, no diagnosis, no prediction, no prescription):

  1. Family & cascade screening — South Asian cardiometabolic risk clusters in
     families, and Lp(a) in particular is largely inherited; when it is elevated,
     guidelines suggest discussing screening of first-degree relatives. Shown when
     the patient indicates South Asian ancestry OR has an elevated Lp(a).
  2. Culturally-tailored prevention support — points to the South Asian Heart
     Center's existing, vetted lifestyle programs. Shown for South Asian ancestry.
     This routes to the center's reviewed content rather than generating any
     personalized lifestyle prescription.

Everything here is informational and framed as "consider discussing with your
clinician." It deliberately avoids prescriptive or diagnostic language.
"""
from __future__ import annotations

from sahc_risklens.clinical.biomarkers import get_field

_LPA_RISK_ENHANCER_MGDL = 50  # 2018 AHA/ACC risk-enhancer threshold (>= 125 nmol/L)


def get_care_navigation(data) -> list[dict]:
    """
    Return CareNavigationItem-shaped dicts (title, description). May be empty when
    nothing applies (e.g., non-South-Asian patient with normal/absent Lp(a)).
    """
    south_asian = bool(get_field(data, "south_asian"))
    lpa = get_field(data, "Lpa_mgdl")
    lpa_high = lpa is not None and lpa >= _LPA_RISK_ENHANCER_MGDL

    items: list[dict] = []

    if south_asian or lpa_high:
        if lpa_high:
            description = (
                "Lipoprotein(a) is largely inherited. When it is elevated, guidelines "
                "suggest discussing screening of first-degree relatives (parents, "
                "siblings, children) with your clinician — sometimes called cascade "
                "screening. Cardiometabolic conditions also tend to cluster in South "
                "Asian families. This is general guidance for discussion, not a diagnosis."
            ) if south_asian else (
                "Lipoprotein(a) is largely inherited. When it is elevated, guidelines "
                "suggest discussing screening of first-degree relatives (parents, "
                "siblings, children) with your clinician — sometimes called cascade "
                "screening. This is general guidance for discussion, not a diagnosis."
            )
        else:
            description = (
                "Cardiometabolic conditions common in South Asian families often cluster "
                "among close relatives. You may wish to ask your clinician whether "
                "first-degree relatives (parents, siblings, children) would benefit from "
                "screening. This is general guidance for discussion, not a diagnosis."
            )
        items.append({"title": "Family & screening", "description": description})

    if south_asian:
        items.append({
            "title": "Culturally-tailored prevention",
            "description": (
                "The South Asian Heart Center offers culturally-tailored, lifestyle-"
                "focused prevention support — diet, activity, and stress guidance adapted "
                "to South Asian contexts. Consider discussing these programs with your "
                "clinician or the center. This is informational, not personalized medical "
                "advice."
            ),
        })

    return items


__all__ = ["get_care_navigation"]
