"""Garde-fou de duree pour la phase de collecte.

Sans cela, un run pouvait depasser le timeout GitHub Actions et se faire tuer
AVANT d'ecrire le moindre fichier : plusieurs heures de scraping pour zero
rapport. Avec un budget, la collecte s'arrete proprement et le rapport est
toujours produit avec ce qui a ete recolte.
"""

import logging
import time

logger = logging.getLogger(__name__)


class Deadline:
    def __init__(self, minutes: float):
        self.limit = max(float(minutes), 0.0) * 60.0
        self.start = time.monotonic()
        self._warned = False

    @property
    def elapsed(self) -> float:
        return time.monotonic() - self.start

    @property
    def remaining(self) -> float:
        return max(self.limit - self.elapsed, 0.0)

    def expired(self) -> bool:
        if self.limit <= 0:
            return False
        over = self.elapsed >= self.limit
        if over and not self._warned:
            self._warned = True
            logger.warning(
                f"Budget de collecte atteint ({self.limit / 60:.0f} min) - "
                f"arret propre, le rapport sera ecrit avec ce qui a ete collecte."
            )
        return over

    def summary(self) -> str:
        return f"{self.elapsed / 60:.1f} min ecoulees sur {self.limit / 60:.0f} min"
