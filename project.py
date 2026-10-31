"""Local revenue, the forward, USD revenue and DSCR."""

import numpy as np

from config import Params


def revenue_local(p: Params) -> np.ndarray:
    """Local-currency revenue for years 1..T, shape (years,).

    Year 1 is normalised to 1. Later years grow at rate `growth`.
    The level is arbitrary: debt_service_usd is scaled off the same
    year-1 revenue, so only growth changes the DSCR profile.
    """
    t = np.arange(1, p.years + 1)
    return (1.0 + p.growth) ** (t - 1)



def debt_service_usd(p: Params) -> float:
    """Flat annual USD debt service, backed out from initial_dscr.

    initial_dscr is the year-1 DSCR you would get by converting
    year-1 local revenue at today's spot s0.
    """
    rev_year1 = revenue_local(p)[0]
    usd_revenue_at_s0 = rev_year1 / p.s0
    return float(usd_revenue_at_s0 / p.initial_dscr)


def forward_rates(p: Params) -> np.ndarray:
    """Forwards locked at t = 0, shape (years,). F(t) for t = 1..T.

    Covered interest parity: F(t) = s0 * exp((r_local - r_usd) * t).
    """
    t = np.arange(1, p.years + 1, dtype=float)
    return p.s0 * np.exp((p.r_local - p.r_usd) * t)


def usd_revenue(fx: np.ndarray, p: Params,
                hedge_ratio: float, hedge_years: int) -> np.ndarray:
    """USD revenue, shape (n_paths, years).

    For years t <= hedge_years, a share hedge_ratio is converted at the
    forward and the rest at the spot. After that, everything is at the spot.
    """
    spots = fx[:, 1:]
    # row vectors, so they broadcast across paths
    rev = revenue_local(p).reshape(1, -1)
    fwd = forward_rates(p).reshape(1, -1)

    usd = rev / spots
    n_hedged = min(int(hedge_years), p.years)
    if n_hedged > 0:
        usd[:, :n_hedged] = (
            hedge_ratio * rev[:, :n_hedged] / fwd[:, :n_hedged]
            + (1.0 - hedge_ratio) * rev[:, :n_hedged] / spots[:, :n_hedged]
        )
    return usd


def dscr(fx: np.ndarray, p: Params,
         hedge_ratio: float, hedge_years: int) -> np.ndarray:
    """DSCR = USD revenue / USD debt service. Shape (n_paths, years)."""
    return usd_revenue(fx, p, hedge_ratio, hedge_years) / debt_service_usd(p)


