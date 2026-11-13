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


JOURNAL_ABBREV = {
    "Annu Int Conf IEEE Eng Med Biol Soc": "Annu. Int. Conf. IEEE Eng. Med. Biol. Soc.",
    "Antioxidants (Basel)": "Antioxidants (Basel)",
    "BMC Med Res Methodol": "BMC Med. Res. Methodol.",
    "Bioinform Adv": "Bioinform. Adv.",
    "Bioinformatics": "Bioinformatics",
    "Biom J": "Biom. J.",
    "Brief Bioinform": "Brief. Bioinform.",
    "Cancer Cell": "Cancer Cell",
    "Cancer Res Commun": "Cancer Res. Commun.",
    "Cancers (Basel)": "Cancers (Basel)",
    "Cell": "Cell",
    "Cell Rep": "Cell Rep.",
    "Comput Biol Chem": "Comput. Biol. Chem.",
    "Diagnostics (Basel)": "Diagnostics (Basel)",
    "Eur J Cancer": "Eur. J. Cancer",
    "Gigascience": "Gigascience",
    "Hum Brain Mapp": "Hum. Brain Mapp.",
    "IEEE J Biomed Health Inform": "IEEE J. Biomed. Health Inform.",
    "Mol Cell": "Mol. Cell",
    "N Biotechnol": "N. Biotechnol.",
    "NAR Genom Bioinform": "NAR Genom. Bioinform.",
    "Nat Biotechnol": "Nat. Biotechnol.",
    "Nat Commun": "Nat. Commun.",
    "Nat Genet": "Nat. Genet.",
    "Nat Methods": "Nat. Methods",
    "Nat Rev Cancer": "Nat. Rev. Cancer",
    "Nucleic Acids Res": "Nucleic Acids Res.",
    "PLoS Biol": "PLoS Biol.",
    "Proc Natl Acad Sci U S A": "Proc. Natl. Acad. Sci. U.S.A.",
    "STAR Protoc": "STAR Protoc.",
    "Stat Med": "Stat. Med.",
    "bioRxiv": "bioRxiv",
}

# Preprints and non-PubMed items, in SAGMB author-date form.
PREPRINT_META = {
    "assaybench": (["De Brouwer", "Edwards", "Wu"], "2026",
                   "De Brouwer, E., Edwards, C., Wu, A., Collier, J., Heimberg, G., Li, X., "
                   "Subramaniam, M., Hajiramezanali, E., et al. (2026). AssayBench: an "
                   "assay-level virtual cell benchmark for LLMs and agents. arXiv:2605.10876 "
                   "[preprint], 11 May 2026. Not peer reviewed."),
    "prosz": (["Prosz", "Sztupinszki", "Diossy"], "2026",
              "Prosz, A.G., Sztupinszki, Z., Diossy, M., Zimon, B., Csabai, I.G., and Szallasi, Z. "
              "(2026). Zero-shot biological reasoning with open-weights large language models "
              "reproduces CRISPR screen based prediction of synthetic lethal interactions. "
              "bioRxiv [preprint] v1, 30 January 2026, doi:10.64898/2026.01.28.702211. Not peer "
              "reviewed; not published."),
    "shamsudheen": (["Shamsudheen", "Hennig"], "2023",
                    "Shamsudheen, M.I. and Hennig, C. (2023). Should we test the model "
                    "assumptions before running a model-based test? J. Data Sci. Stat. Vis. "
                    "3: 1-40, doi:10.52933/jdssv.v3i3.73."),
}


TITLE_SENTENCE_CASE = {
    "musl": "MuSL: multimodal deep learning for generalizable prediction of synthetic lethality from sequence, transcriptomic, and network data",
    "feng": "Benchmarking machine learning methods for synthetic lethality prediction in cancer",
    "feng_corr": "Author correction: benchmarking machine learning methods for synthetic lethality prediction in cancer",
    "anyaso": "Can the unit size predict outcomes? Testing for informativeness in three-level designs",
    "horlbeck": "Mapping the genetic landscape of human cells",
    "kim_ics": "Test statistics and statistical inference for data with informative cluster sizes",
    "lai": "Inferring drug-gene relationships in cancer using literature-augmented large language models",
    "leakbrain": "A reproducible benchmark for leakage-resistant machine learning on multi-site brain connectivity graphs",
    "leakfood": "Leakage-aware machine learning and deep learning benchmarking of food antioxidant capacity prediction on the Antioxidant Food Table",
    "shao": "CRISPR-Cas9 genome and double-knockout screening to identify novel therapeutic targets for chemoresistance in triple-negative breast cancer",
    "slmerk": "SL-MERK: synthetic lethality mechanism explainer based on GraphRAG and knowledge graph",
    "zhao": "Combinatorial CRISPR-Cas9 metabolic screens reveal critical redox control points dependent on the KEAP1-NRF2 regulatory axis",
}


def _split_name(name: str) -> tuple[str, str]:
    """'Ryan CJ' -> ('Ryan', 'C.J.'); handles multi-word surnames."""
    parts = name.split()
    if len(parts) > 1 and re.fullmatch(r"[A-Z]{1,3}", parts[-1]):
        surname, initials = " ".join(parts[:-1]), parts[-1]
        return surname, ".".join(initials) + "."
    return name, ""


def _surnames(r: dict) -> list[str]:
    return [_split_name(a)[0] for a in (r.get("authors") or ["Anonymous"])]


def intext(surnames: list[str], year: str) -> str:
    if len(surnames) == 1:
        who = surnames[0]
    elif len(surnames) == 2:
        who = f"{surnames[0]} and {surnames[1]}"
    else:
        who = f"{surnames[0]} et al."
    return f"{who}, {year}"


def sagmb_ref(r: dict, key: str = "") -> str:
    """Author(s) (Year). Title. Journal Abbrev. volume: pages, doi."""
    au = r.get("authors") or ["Anonymous"]
    shown = au[:8]
    fmt = []
    for a in shown:
        s, i = _split_name(a)
        fmt.append(f"{s}, {i}" if i else s)
    if len(au) > 8:
        names = ", ".join(fmt) + ", et al."
    elif len(fmt) == 1:
        names = fmt[0]
    else:
        names = ", ".join(fmt[:-1]) + ", and " + fmt[-1]
    title = TITLE_SENTENCE_CASE.get(key) or r["title"].rstrip(".")
    jr = JOURNAL_ABBREV.get(r["journal"], r["journal"])
    out = f"{names} ({r['year']}). {title}. {jr}"
    if r.get("volume") and r["volume"].isdigit():
        out += f" {r['volume']}"
        if r.get("pages"):
            out += f": {r['pages']}"
    out = out.rstrip()
    if r.get("doi"):
        out += f", doi:{r['doi']}"
    out += "."
    if key == "feng":
        # The benchmark carries a published author correction; cite the article, flag the correction.
        out += (" Author correction: Nat. Commun. 16: 1619 (2025), "
                "doi:10.1038/s41467-025-56368-x.")
    return out


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

    # --- citations: SAGMB author-date style ----------------------------------
    used: set[str] = set()

    def meta(key: str):
        if key in PREPRINT_META:
            sn, yr, _ = PREPRINT_META[key]
            return sn, yr
        if key not in K2P:
            raise SystemExit(f"FAIL: unknown citation key '{key}'")
        r = REC[K2P[key]]
        return _surnames(r), r["year"]

    def render_run(m) -> str:
        keys = re.findall(r"\[\[cite:([a-z0-9_]+)\]\]", m.group(0))
        bits = []
        for k in keys:
            used.add(k)
            sn, yr = meta(k)
            bits.append(intext(sn, yr))
        return "(" + "; ".join(bits) + ")"

    # a run of adjacent markers becomes one parenthesis
    text = re.sub(r"(?:\[\[cite:[a-z0-9_]+\]\])+", render_run, text)

    entries = []
    for key in sorted(used):
        if key in PREPRINT_META:
            sn, yr, full = PREPRINT_META[key]
            entries.append((sn[0], yr, full))
        else:
            r = REC[K2P[key]]
            entries.append((_surnames(r)[0], r["year"], sagmb_ref(r, key)))
    entries.sort(key=lambda e: (e[0].lower(), e[1]))
    text = text.replace("{{REFERENCES}}", "\n".join(f"{e[2]}\n" for e in entries))

    leftover = re.findall(r"\{\{[A-Z_]+\}\}|\[\[cite:[^\]]+\]\]|<<[a-z]+>>", text)
    if leftover:
        raise SystemExit("FAIL: unresolved placeholders: " + ", ".join(sorted(set(leftover))))

    out_path.write_text(text)
    words = len(re.findall(r"\b[\w'-]+\b", text))
    print(f"wrote {out_path} — {len(entries)} references, ~{words} words (whole file)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
