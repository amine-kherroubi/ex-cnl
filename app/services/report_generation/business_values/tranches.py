from __future__ import annotations

"""
Constantes définissant les types de tranches de paiement pour l'habitat rural.

Ce module contient les ensembles de tranches utilisées pour déterminer
les lancements (première tranche) et livraisons (dernière tranche) dans
les rapports d'activité mensuelle.

Les tranches de paiement suivent le système de financement progressif :
- Première tranche : Correspond au lancement d'un projet de logement
- Dernière tranche : Correspond à l'achèvement/livraison d'un projet

Ces constantes sont utilisées dans les requêtes SQL pour classifier
les paiements selon leur phase dans le cycle de vie du projet.
"""

# Tranches correspondant aux lancements (première tranche de paiement)
# Ces tranches indiquent le démarrage effectif d'un projet de logement
TRANCHES_LANCEMENT: set[str] = {
    "20%  1 ERE TRANCHE",  # Première tranche de 20%
    "60%  Première Tranche",  # Première tranche de 60%
    "40%  Première Tranche",  # Première tranche de 40%
    "60%  1+2 EME TRANCHE",  # Combinaison des deux premières tranches
    "100%  Tranche totale",  # Paiement intégral en une fois
    "100%  1+2+3 EME TRANCHE",  # Toutes les tranches combinées
}

# Tranches correspondant aux livraisons (dernière tranche de paiement)
# Ces tranches indiquent l'achèvement complet d'un projet de logement
TRANCHES_LIVRAISON: set[str] = {
    "40%  3 EME TRANCHE",  # Troisième et dernière tranche de 40%
    "40%  Deuxième Tranche",  # Deuxième tranche finale de 40%
    "80%  2+3 EME TRANCHE",  # Combinaison des tranches finales
    "40%  C2",  # Complément final de 40%
    "60%  Deuxième Tranche",  # Deuxième tranche finale de 60%
    "Tranche complémentaire 2",  # Complément final
    "100%  Tranche totale",  # Paiement intégral en une fois
    "100%  1+2+3 EME TRANCHE",  # Toutes les tranches combinées
    "40%  2 EME TRANCHE",  # Deuxième tranche de 40%
}
