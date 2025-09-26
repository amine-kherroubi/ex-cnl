from __future__ import annotations

# Standard library imports
from typing import Final

TRANCHES_DE_LANCEMENT: Final[set[str]] = {
    "20%  1 ERE TRANCHE",
    "60%  Première Tranche",
    "40%  Première Tranche",
    "60%  1+2 EME TRANCHE",
    "100%  Tranche totale",
    "100%  1+2+3 EME TRANCHE",
}

TRANCHES_DE_LIVRAISON: Final[set[str]] = {
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
