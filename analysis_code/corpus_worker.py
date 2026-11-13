"""Stream the PubMed 2026 annual baseline into a compact, BM25-exact index for the pilot.

For every eligible record (Entrez date <= cutoff, not on the exclusion list) we keep
the true token length and, for documents that mention at least one SLKB gene symbol,
the term frequencies of those gene tokens only. Because the registered unconditioned
ranker queries a single gene token, this preserves n, avgdl, df/idf of every gene
token and tf/dl of every document that can score > 0, so BM25 scores are identical
to the registered BM25Index built over the full snapshot. Parsing uses the staged
CC-02 converter's record reader (Entrez-date rule, decision A6/C6, PROPOSED).
"""
import sys, os, json, gzip, hashlib, pickle, subprocess, time, csv
from collections import Counter
from pathlib import Path
from multiprocessing import Pool
sys.path.insert(0, "/mnt/project-files/PROJECT1_FINAL_PRE_GATE3_PACKAGE/01_Staging_CC02")
sys.path.insert(0, "/mnt/project-files/06_Implementation")
import pubmed_to_jsonl as conv
from brca_rag.corpus import tokenise

BASE = "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/"
CUTOFF = "2016-02-09"
HERE = Path(__file__).resolve().parent
OUT = HERE / "corpus_parts"; OUT.mkdir(exist_ok=True)
TMP = HERE / "dl"; TMP.mkdir(exist_ok=True)
GENES = {g.lower() for g in json.load(open(HERE / "genes_all.json"))}
EXCL = set()
for row in csv.DictReader(open("/mnt/project-files/04_Gate2B_Resolution/leakage_exclusion_list.csv")):
    for f in ("pmid", "doi"):
        v = (row.get(f) or "").strip()
        if v: EXCL.add(v)

def fetch(name):
    for attempt in range(5):
        r1 = subprocess.run(["curl", "-sS", "-f", "-o", str(TMP / name), BASE + name])
        r2 = subprocess.run(["curl", "-sS", "-f", BASE + name + ".md5"], capture_output=True, text=True)
        if r1.returncode == 0 and r2.returncode == 0:
            want = r2.stdout.strip().split("=")[-1].strip()
            got = hashlib.md5(open(TMP / name, "rb").read()).hexdigest()
            if want == got:
                return want
        time.sleep(2 ** attempt)
    raise RuntimeError(f"download/md5 failed for {name}")

def work(i):
    name = f"pubmed26n{i:04d}.xml.gz"
    part = OUT / f"{i:04d}.pkl"
    if part.exists():
        return i, "cached"
    md5 = fetch(name)
    path = TMP / name
    sha = conv.file_sha256(path)
    st = Counter(); df = Counter(); total_len = 0; n = 0
    docs = []; digests = []; rejects = Counter(); deleted = []
    for pmid, rec, why in conv._records(path):
        st["records"] += 1
        if why == "deleted":
            deleted.append(pmid); continue
        if rec is None:
            rejects[why] += 1; continue
        if pmid in EXCL:
            st["dropped_excluded"] += 1; st["excluded_entrez_" + rec["published"]] += 1; continue
        if rec["published"] > CUTOFF:
            st["dropped_after_cutoff"] += 1; continue
        text = f'{rec["title"]}\n{rec["abstract"]}'
        toks = tokenise(text)
        dl = len(toks); n += 1; total_len += dl
        g = Counter(t for t in toks if t in GENES)
        if g:
            df.update(g.keys())
            docs.append((pmid, rec["published"], dl, dict(g)))
        digests.append((pmid, hashlib.sha256((pmid + "|" + rec["published"] + "|" + text).encode()).hexdigest()))
    os.remove(path)
    res = dict(file=name, md5=md5, sha256=sha, n_eligible=n, total_len=total_len, df=dict(df),
               docs=docs, digests=digests, stats=dict(st), rejects=dict(rejects), deleted=deleted)
    with open(str(part) + ".tmp", "wb") as fh:
        pickle.dump(res, fh)
    os.replace(str(part) + ".tmp", part)
    return i, n

if __name__ == "__main__":
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    t0 = time.time(); done = 0
    with Pool(int(sys.argv[3]) if len(sys.argv) > 3 else 4) as pool:
        for i, n in pool.imap_unordered(work, range(lo, hi + 1)):
            done += 1
            print(f"{time.strftime('%H:%M:%S')} file {i} eligible={n} done={done} elapsed={time.time()-t0:.0f}s", flush=True)
