"""Three hedge policies, then a volatility sweep. Writes a table and two figures."""

from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # save files, dont open a window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from checks import run_checks
from config import Params
from metrics import breach_probability, min_dscr_quantile
from project import dscr
from simulate import simulate_fx_paths

# same random paths are reused across the three policies
SCENARIOS = {
    "Unhedged":          dict(hedge_ratio=0.0, hedge_years=0),
    "Fully hedged":      dict(hedge_ratio=1.0, hedge_years=10),
    "Hedged 3 yrs only": dict(hedge_ratio=1.0, hedge_years=3),
}

SIGMAS = [0.10, 0.15, 0.20, 0.30]

COLOURS = {
    "Unhedged": "#1f4e79",
    "Fully hedged": "#2e7d32",
    "Hedged 3 yrs only": "#c65911",
}

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"


def scenario_table(p: Params, fx) -> tuple[pd.DataFrame, dict]:
    """Metrics for each hedge, on one shared set of FX paths."""
    rows = []
    lowest = {}
    for name, hedge in SCENARIOS.items():
        cover = dscr(fx, p, **hedge)
        prob, se = breach_probability(cover)
        q05 = min_dscr_quantile(cover, q=0.05)
        rows.append({
            "scenario": name,
            "breach_probability": prob,
            "standard_error": se,
            "min_dscr_p05": q05,
        })
        lowest[name] = cover.min(axis=1)
    return pd.DataFrame(rows), lowest


def sensitivity_table(p: Params) -> pd.DataFrame:
    """Breach probability and the 5% DSCR quantile on a grid of sigma.

    Each sigma is simulated once. The three hedges then share those paths,
    so the gap between lines is the hedge, not a new draw of random numbers.
    """
    rows = []
    for sigma in SIGMAS:
        p_sig = replace(p, sigma=sigma)
        fx = simulate_fx_paths(p_sig)
        for name, hedge in SCENARIOS.items():
            cover = dscr(fx, p_sig, **hedge)
            prob, se = breach_probability(cover)
            rows.append({
                "sigma": sigma,
                "scenario": name,
                "breach_probability": prob,
                "standard_error": se,
                "min_dscr_p05": min_dscr_quantile(cover, q=0.05),
            })
    return pd.DataFrame(rows)


def plot_min_dscr(lowest: dict, path: Path) -> None:
    """Cumulative distribution of the lowest DSCR on each path."""
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, values in lowest.items():
        xs = np.sort(values)
        ys = np.arange(1, len(xs) + 1) / len(xs)
        ax.plot(xs, ys, color=COLOURS[name], label=name, linewidth=1.8)

    ax.axvline(1.0, color="black", linestyle="--", linewidth=1, label="DSCR = 1")
    ax.set_xlabel("Lowest DSCR on the path")
    ax.set_ylabel("Cumulative probability")
    ax.set_title("Distribution of the lowest DSCR")
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_sensitivity(sens: pd.DataFrame, path: Path) -> None:
    """Breach probability against volatility, one line per hedge."""
    fig, ax = plt.subplots(figsize=(8, 5))
    for name in SCENARIOS:
        part = sens[sens["scenario"] == name]
        ax.errorbar(
            part["sigma"] * 100,
            part["breach_probability"] * 100,
            yerr=part["standard_error"] * 100,
            color=COLOURS[name],
            marker="o",
            capsize=3,
            linewidth=1.8,
            label=name,
        )
    ax.set_xlabel("Exchange-rate volatility (%)")
    ax.set_ylabel("DSCR breach probability (%)")
    ax.set_title("DSCR breach probability and volatility")
    ax.set_xticks([s * 100 for s in SIGMAS])
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    run_checks()

    p = Params()
    # baseline sigma. One simualtion, three ways of hedging it.
    fx = simulate_fx_paths(p)
    table, lowest = scenario_table(p, fx)
    sens = sensitivity_table(p)

    print()
    print(table.to_string(index=False))
    print()
    print(sens.to_string(index=False))

    table.to_csv(ROOT / "results_baseline.csv", index=False)

    FIG.mkdir(exist_ok=True)
    plot_min_dscr(lowest, FIG / "min_dscr_cdf.png")
    plot_sensitivity(sens, FIG / "dscr_breach_probability.png")
    print()
    print(f"Figures saved in {FIG}")


if __name__ == "__main__":
    main()
