"""Sanity checks. Run these before reading any results."""

from dataclasses import replace

import numpy as np

from config import Params
from project import dscr
from simulate import simulate_fx_paths


def run_checks() -> None:
    p = Params()
    fx = simulate_fx_paths(p)

    # E[S(T)] = s0 * exp(mu * T). A missing -sigma^2/2 term
    # shows up as a gap of many standard errors.
    terminal = fx[:, -1]
    mean_hat = float(terminal.mean())
    expected = p.s0 * np.exp(p.mu * p.years)
    se = float(terminal.std(ddof=1) / np.sqrt(terminal.size))
    gap = abs(mean_hat - expected) / se
    assert gap < 5, (
        f"mean S(T) = {mean_hat:.4f}, formula {expected:.4f}, "
        f"gap {gap:.2f} s.e."
    )

    # sigma = 0: the random term drops out, so every path is the same
    p0 = replace(p, sigma=0.0)
    fx0 = simulate_fx_paths(p0)
    assert np.allclose(fx0, fx0[0]), "sigma = 0 should give identical paths"

    # full hedge: DSCR does not depend on the path
    full = dscr(fx, p, hedge_ratio=1.0, hedge_years=p.years)
    assert np.allclose(full, full[0]), "full hedge should kill path risk"

    # hedge_ratio = 0 has to match a hedge window of zero
    ratio_zero = dscr(fx, p, hedge_ratio=0.0, hedge_years=p.years)
    unhedged = dscr(fx, p, hedge_ratio=0.0, hedge_years=0)
    assert np.allclose(ratio_zero, unhedged), "hedge_ratio = 0 did nothing"

    # year 1, no vol, drift equal to the interest differential:
    # the spot lands on the forward, so the hedge does not change DSCR
    p_det = replace(p, sigma=0.0, mu=p.r_local - p.r_usd)
    fx_det = simulate_fx_paths(p_det)
    hedged = dscr(fx_det, p_det, hedge_ratio=1.0, hedge_years=p_det.years)
    open_fx = dscr(fx_det, p_det, hedge_ratio=0.0, hedge_years=0)
    assert np.allclose(hedged[:, 0], open_fx[:, 0]), (
        "year-1 DSCR should match when mu equals the interest spread"
    )

    # column 0 is today, on every path
    assert fx.shape == (p.n_paths, p.years + 1)
    assert np.allclose(fx[:, 0], p.s0), "column 0 should equal s0"

    print(
        f"mean S(T) = {mean_hat:.4f}, formula {expected:.4f} "
        f"({gap:.2f} s.e.)"
    )
    print("All checks passed.")


if __name__ == "__main__":
    run_checks()
