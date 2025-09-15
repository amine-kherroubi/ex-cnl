from __future__ import annotations

# Payment tranches corresponding to project launches (first payment tranche)
# These tranches indicate the effective start of a housing project
LAUNCH_TRANCHES: set[str] = {
    "20%  1 ERE TRANCHE",
    "60%  Première Tranche",
    "40%  Première Tranche",
    "60%  1+2 EME TRANCHE",
    "100%  Tranche totale",
    "100%  1+2+3 EME TRANCHE",
}

# Payment tranches corresponding to deliveries (last payment tranche)
# These tranches indicate the complete completion of a housing project
DELIVERY_TRANCHES: set[str] = {
    "40%  3 EME TRANCHE",
    "40%  Deuxième Tranche",
    "80%  2+3 EME TRANCHE",
    "40%  C2",
    "60%  Deuxième Tranche",
    "Tranche complémentaire 2",
    "100%  Tranche totale",
    "100%  1+2+3 EME TRANCHE",
    "40%  2 EME TRANCHE",
}
