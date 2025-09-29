# Standard library imports
from typing import Final, Set


TRANCHES_DE_LANCEMENT: Final[Set[str]] = {
    "60%  1+2 EME TRANCHE ",
    "20%  1 ERE TRANCHE ",
    "100%  Tranche totale",
    "60%  Première Tranche",
    "100%  1+2+3 EME TRANCHE ",
    "40%  Première Tranche",
}

TRANCHES_DE_LIVRAISON: Final[Set[str]] = {
    "100%  Tranche totale",
    "100%  1+2+3 EME TRANCHE ",
    "40%  3 EME TRANCHE ",
    "40%  Deuxième Tranche",
    "80%  2+3 EME TRANCHE ",
    "40%  C2",
    "60%  Deuxième Tranche",
    "Tranche complémentaire 2",
}

AUTRES_TRANCHES: Final[Set[str]] = {
    "40%  2 EME TRANCHE ",
    "100%  La Complémentaire 1,2 ET 3 ",
    "20%  C1",
    "20%  La Complémentaire 1 ",
    "60%  La Complémentaire 1 ET 2 ",
    "Tranche complémentaire ",
}
