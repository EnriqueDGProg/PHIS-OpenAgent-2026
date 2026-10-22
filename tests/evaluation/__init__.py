"""Automated adversarial evaluation suite for PHIS Open Agent.

Covers missing data, coverage boundaries, source conflicts, window consistency,
question ambiguity, spurious associations, causality rejection, hallucinated IDs,
clinical advice abstention, tool failures/timeouts, determinism, and audit lineage.
"""

__all__ = [
    "validate_investigation_contract",
    "AdversarialEvaluator",
    "JuryAcceptanceMatrix",
    "build_investigation_response",
]
