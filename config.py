# Author: Yuxuan Ma
# Email: matt.ma.24@ucl.ac.uk
#
# All the assumtions sit on Params. Change a number here,
# the functions can stay as they are

from dataclasses import dataclass


@dataclass
class Params:
    s0: float = 1.0                 # local currency per 1 USD
    r_usd: float = 0.04
    r_local: float = 0.08
    mu: float = 0.04                # set equal to r_local - r_usd
    sigma: float = 0.15
    growth: float = 0.03            # growth of local-currency revenue
    initial_dscr: float = 1.3
    years: int = 10
    n_paths: int = 10_000
    seed: int = 888888





