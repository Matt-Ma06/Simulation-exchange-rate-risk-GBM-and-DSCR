"""DSCR breach probability and the tail of the lowest DSCR.

A breach is a year with DSCR < 1: cover is short that year. It is not
a default. Projects usually keep a debt-service reserve for that.
"""

import numpy as np


def breach_probability(dscr: np.ndarray) -> tuple[float, float]:
    """Share of paths with at least one year of DSCR < 1, and its s.e.

    The standard error is the usual Bernoulli one, sqrt(p(1-p)/n).
    """
    breaches = np.any(dscr < 1.0, axis=1)
    prob = float(np.mean(breaches))
    n = breaches.shape[0]
    se = float(np.sqrt(prob * (1.0 - prob) / n))
    return prob, se


def min_dscr_quantile(dscr: np.ndarray, q: float = 0.05) -> float:
    """Take the lowest DSCR on each path, then the q quantile of those."""
    lowest = np.min(dscr, axis=1)
    return float(np.quantile(lowest, q))





