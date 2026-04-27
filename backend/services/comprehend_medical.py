import boto3
import os

comprehend_medical = boto3.client("comprehendmedical", region_name=os.getenv("AWS_REGION", "us-east-1"))

MAX_TEXT_CHARS = 10_000  # Comprehend Medical hard limit is 20K; we cap at 10K for safety

async def extract_medications(text: str) -> list[str]:
    """Extract medication names from clinical text using Comprehend Medical."""
    response = comprehend_medical.detect_entities_v2(Text=text[:MAX_TEXT_CHARS])
    return [
        entity["Text"]
        for entity in response["Entities"]
        if entity["Category"] == "MEDICATION"
    ]

async def check_drug_interactions(medications: list[str]) -> list[dict]:
    """Check for drug interactions using Comprehend Medical RxNorm linking."""
    if len(medications) < 2:
        return []

    text = ", ".join(medications)[:MAX_TEXT_CHARS]
    response = comprehend_medical.infer_rx_norm(Text=text)

    rx_concepts = []
    for entity in response["Entities"]:
        if entity.get("RxNormConcepts"):
            top = entity["RxNormConcepts"][0]
            rx_concepts.append({
                "medication":   entity["Text"],
                "rxnorm_code":  top["Code"],
                "description":  top["Description"],
            })

    return _flag_interactions(rx_concepts)

def _flag_interactions(rx_concepts: list[dict]) -> list[dict]:
    """Flag known high-risk drug combinations."""
    HIGH_RISK_PAIRS = [
        ("warfarin",  "aspirin"),
        ("ssri",      "maoi"),
        ("metformin", "contrast dye"),
        ("digoxin",   "amiodarone"),
    ]
    interactions = []
    names = [c["medication"].lower() for c in rx_concepts]
    for drug_a, drug_b in HIGH_RISK_PAIRS:
        if any(drug_a in n for n in names) and any(drug_b in n for n in names):
            interactions.append({
                "severity": "HIGH",
                "drugs":    [drug_a, drug_b],
                "warning":  f"Potential interaction between {drug_a} and {drug_b}. Review dosing carefully.",
            })
    return interactions
