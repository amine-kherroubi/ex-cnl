from __future__ import annotations

"""
Constantes définissant les types de tranches de paiement pour l'habitat rural.

Ce module contient les ensembles de tranches utilisées pour déterminer
les lancements (première tranche) et livraisons (dernière tranche) dans
les rapports d'activité mensuelle.
"""

# Tranches correspondant aux lancements (première tranche de paiement)
TRANCHES_LANCEMENT: set[str] = {
    "20%  1 ERE TRANCHE",
    "60%  Première Tranche",
    "40%  Première Tranche",
    "60%  1+2 EME TRANCHE",
    "100%  Tranche totale",
    "100%  1+2+3 EME TRANCHE",
}

# Tranches correspondant aux livraisons (dernière tranche de paiement)
TRANCHES_LIVRAISON: set[str] = {
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
