#!/usr/bin/env python3
"""Assemble the manuscript: substitute every {{TOKEN}} and resolve every [[cite:key]].

Fails loudly if any token or any citation key is left unresolved, so an incomplete
manuscript cannot be produced silently.

Usage: python3 fill.py <pilot_report_REAL.json> <out.md>
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEC = HERE / "sections"
REFS = json.load(open(HERE.parent / "lit" / "verified_refs_2026-10-31.json"))
REC, K2P = REFS["records"], REFS["key_to_pmid"]

# Two preprints verified directly from the arXiv and bioRxiv APIs on 31 Oct 2026
# (they have no PubMed record, so they are not in the PubMed-verified file).
PREPRINTS = {
    "assaybench": ("De Brouwer E, Edwards C, Wu A, Collier J, Heimberg G, Li X, Subramaniam M, "
                   "Hajiramezanali E, Richmond D, Hütter JC, Mostafavi S, Scalia G, et al. "
                   "AssayBench: An Assay-Level Virtual Cell Benchmark for LLMs and Agents. "
                   "arXiv:2605.10876 [preprint]. 11 May 2026. Not peer reviewed."),
    "prosz": ("Prosz AG, Sztupinszki Z, Diossy M, Zimon B, Csabai IG, Szallasi Z. "
              "Zero-shot biological reasoning with open-weights large language models reproduces "
              "CRISPR screen based prediction of synthetic lethal interactions. bioRxiv [preprint] "
              "v1, 30 January 2026. doi:10.64898/2026.01.28.702211. Not peer reviewed; not "
              "published."),
    "shamsudheen": ("Shamsudheen MI, Hennig C. Should we test the model assumptions before running "
                    "a model-based test? J Data Sci Stat Vis. 2023;3(3):1-40. "
                    "doi:10.52933/jdssv.v3i3.73. Preprint: arXiv:1908.02218."),
}


def vancouver(r: dict) -> str:
    au = r.get("authors") or []
    names = ", ".join(au[:6]) + (", et al" if len(au) > 6 else "")
    bits = [f"{names}. {r['title'].rstrip('.')}. {r['journal']}. {r['year']}"]
    if r.get("volume"):
        v = r["volume"] + (f"({r['issue']})" if r.get("issue") else "")
        bits.append(f";{v}")
    if r.get("pages"):
        bits.append(f":{r['pages']}")
    s = "".join(bits) + "."
    if r.get("doi"):
        s += f" doi:{r['doi']}."
    s += f" PMID: {r['pmid']}."
    return s


def main() -> int:
    rep = json.load(open(sys.argv[1]))
    out_path = Path(sys.argv[2])
    text = (HERE / "manuscript_template.md").read_text()

    vc = rep["variance_components"]
    e = vc["eligible_screens_protocol_2_1"]
    sh = vc["cluster_value_shape_eligible"]
    cm = rep["corpus"]

    pilot = (SEC / "RESULTS_PILOT.md").read_text()
    abs_res = (SEC / "ABS_RESULTS.md").read_text()
    abs_con = (SEC / "ABS_CONCLUSION.md").read_text()

    fmt = {
        "G": e["G_cell_models"],
        "gword": {5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
                  10: "ten"}.get(e["G_cell_models"], str(e["G_cell_models"])),
        "nq": f"{e['n_queries']:,}",
        "mean": f"{e['mean_difference']:+.4f}", "sd": f"{e['sd_between_cell_models_point']:.4f}",
        "sdlo": f"{e['sd_between_cell_models_ci95'][0]:.4f}",
        "sdhi": f"{e['sd_between_cell_models_ci95'][1]:.4f}",
        "ucl": f"{e['sd_between_cell_models_ucl80']:.4f}",
        "icc": f"{e['rho_icc_point']:.3f}",
        "icclo": f"{e['rho_icc_ci95'][0]:.4f}", "iccci": f"{e['rho_icc_ci95'][1]:.4f}",
        "neff": f"{e['n_effective']:.1f}",
        "det": f"{e['detectable_difference_at_point_sd']:.4f}",
        "detu": f"{e['detectable_difference_at_ucl80']:.4f}",
        "skew": ("not estimable" if sh["skewness_sample"] is None else f"{sh['skewness_sample']:+.2f}"),
        "ndocs": f"{cm['n_documents']:,}", "nfiles": f"{cm['n_files']:,}",
        "cutoff": cm["cutoff"],
    }
    # typographic minus sign for negative values, so the proof reads as print
    fmt = {k: (v.replace("-", "\u2212", 1) if isinstance(v, str) and v.startswith("-") else v)
           for k, v in fmt.items()}
    for k, v in fmt.items():
        tok = "<<%s>>" % k
        pilot = pilot.replace(tok, str(v))
        abs_res = abs_res.replace(tok, str(v))
        abs_con = abs_con.replace(tok, str(v))

    blocks = {
        "ABS_RESULTS": abs_res.strip(), "ABS_CONCLUSION": abs_con.strip(),
        "RESULTS_PILOT": pilot.strip(),
    }
    for name in ("INTRODUCTION", "RELATED_WORK", "METHODS",
                 "RESULTS_AUDIT", "RESULTS_DESIGN", "RESULTS_INFERENCE", "RESULTS_STATUS",
                 "DISCUSSION", "CONCLUSIONS", "DECLARATIONS",
                 "FIGURE_LEGENDS", "TABLE_LEGENDS"):
        blocks[name] = (SEC / f"{name}.md").read_text().strip()

    for name, body in blocks.items():
        text = text.replace("{{%s}}" % name, body)

    # --- citations, numbered in order of first appearance -------------------
    order: list[str] = []

    def numfor(key: str) -> int:
        if key not in order:
            if key not in K2P and key not in PREPRINTS:
                raise SystemExit(f"FAIL: unknown citation key '{key}'")
            order.append(key)
        return order.index(key) + 1

    text = re.sub(r"\[\[cite:([a-z0-9_]+)\]\]", lambda m: f"[{numfor(m.group(1))}]", text)

    lines = []
    for i, key in enumerate(order, 1):
        if key in PREPRINTS:
            lines.append(f"{i}. {PREPRINTS[key]}")
        else:
            lines.append(f"{i}. {vancouver(REC[K2P[key]])}")
    text = text.replace("{{REFERENCES}}", "\n".join(lines))

    # Collapse adjacent citation markers: [4][5][6][7] -> [4-7]; [8][9] -> [8,9]
    def _collapse(m):
        nums = sorted({int(x) for x in re.findall(r"\d+", m.group(0))})
        parts, i = [], 0
        while i < len(nums):
            j = i
            while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
                j += 1
            if j - i >= 2:
                parts.append(f"{nums[i]}-{nums[j]}")
            else:
                parts.extend(str(n) for n in nums[i:j + 1])
            i = j + 1
        return "[" + ",".join(parts) + "]"

    text = re.sub(r"\[\d+\](?:\[\d+\])+", _collapse, text)

    leftover = re.findall(r"\{\{[A-Z_]+\}\}|\[\[cite:[^\]]+\]\]|<<[a-z]+>>", text)
    if leftover:
        raise SystemExit("FAIL: unresolved placeholders: " + ", ".join(sorted(set(leftover))))

    out_path.write_text(text)
    words = len(re.findall(r"\b[\w'-]+\b", text))
    print(f"wrote {out_path} — {len(order)} references, ~{words} words (whole file)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
