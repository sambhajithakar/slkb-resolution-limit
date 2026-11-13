#!/usr/bin/env python3
"""STAGED power recalculation from the real pilot differences.

This runs CC-02 staged code (`brca_rag_cc02.covariance`, `.power`), which is
**not registered**. It therefore produces a STAGED result: the recalculated
planning figure is reported with that label everywhere and is not treated as
final until the researcher approves CC-02.

It tests no hypothesis and reads only the pilot's paired differences and the
eligible-screen table.

Usage:
  python3 power_recalc_staged.py <paired_differences.csv> <screen_table.csv> <out.json>
"""
from __future__ import annotations
import json, sys
from pathlib import Path

import pandas as pd

STAGED = "/mnt/project-files/PROJECT1_FINAL_PRE_GATE3_PACKAGE/01_Staging_CC02"
sys.path.insert(0, STAGED)
from brca_rag_cc02 import covariance, power  # noqa: E402

ELIGIBLE = {("26864203", "OVCAR8"), ("28319085", "K562"), ("28319113", "293T"),
            ("28319113", "A549"), ("28319113", "HELA"), ("29452643", "A549"),
            ("29452643", "HELA"), ("30033366", "JURKAT"), ("30033366", "K562"),
            ("33956155", "RPE1"), ("36060092", "22RV1")}


def main() -> int:
    diff = pd.read_csv(sys.argv[1], dtype={"study": str})
    st = pd.read_csv(sys.argv[2], dtype={"study": str})
    elig = diff[[(s, c) in ELIGIBLE for s, c in zip(diff.study, diff.cell_line)]].copy()
    if elig.empty:
        raise SystemExit("FAIL: no eligible rows — check the study/cell_line keys")

    cov = covariance.covariance_report(elig)
    sd_pt = cov["sd_between_cell_models"]["point"]
    # the registered 80% one-sided upper limit on an SD, chi-square form
    import numpy as np
    from scipy import stats as sps
    G = cov["G_cell_models"]
    sd_ucl = float(sd_pt * np.sqrt((G - 1) / sps.chi2.ppf(0.20, G - 1)))

    rec = power.recalculate(st, sd_point=sd_pt, sd_upper_limit=sd_ucl,
                            rho_within_study=cov["rho_within_study"],
                            rho_shared_line=cov["rho_shared_line"])
    out = {
        "status_of_this_result": ("STAGED — produced by CC-02 code that is staged, not registered. "
                                  "It is not a final planning figure until CC-02 is approved."),
        "what_this_is_not": "not a hypothesis test, not a confirmatory quantity, not a measured effect",
        "covariance_report": cov,
        "power_recalculation": rec,
    }
    Path(sys.argv[3]).write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(rec, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
