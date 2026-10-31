"""Simulate the exchange rate with geometric Brownian motion."""

import numpy as np

from config import Params


def simulate_fx_paths(p: Params) -> np.ndarray:
    """FX paths, shape (n_paths, years + 1). Column 0 is s0.

    S is local currency per 1 USD, so a rise in S is a depreciation
    of the local currency. Annual step of the log:
    (mu - sigma^2/2) * dt + sigma * sqrt(dt) * Z.
    """
    rng = np.random.default_rng(p.seed)
    # one standard normal per path, per year
    z = rng.standard_normal((p.n_paths, p.years))

  # dt is one year, so sqrt(dt) happens to be 1. Write it out anyway.
    dt = 1.0
    log_step = (p.mu - 0.5 * p.sigma ** 2) * dt + p.sigma * np.sqrt(dt) * z
    # cumulate along time (axis 1), not down the paths
    log_s = np.cumsum(log_step, axis=1)
    future = p.s0 * np.exp(log_s)

    today = np.full((p.n_paths, 1), p.s0)
    return np.hstack([today, future])
