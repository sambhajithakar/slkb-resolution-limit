import json, subprocess, urllib.parse, time, xml.etree.ElementTree as ET
Q = {
 "Q1_SL_LLM_RAG_agent": '("synthetic lethal"[tiab] OR "synthetic lethality"[tiab]) AND ("large language model"[tiab] OR "language model"[tiab] OR "retrieval-augmented"[tiab] OR "retrieval augmented"[tiab] OR agent[tiab] OR agentic[tiab] OR "knowledge graph"[tiab])',
 "Q2_SL_prediction_benchmark_leakage": '("synthetic lethal"[tiab] OR "synthetic lethality"[tiab]) AND (prediction[tiab] OR predict*[tiab]) AND (benchmark*[tiab] OR leakage[tiab] OR generaliz*[tiab] OR "cold-start"[tiab] OR "data split"[tiab])',
 "Q3_context_specific_SL": '("synthetic lethal"[tiab] OR "synthetic lethality"[tiab]) AND ("cell line-specific"[tiab] OR "context-specific"[tiab] OR "context-dependent"[tiab] OR "cell-line-specific"[tiab] OR "genetic context"[tiab])',
 "Q4_RAG_target_discovery_cancer": '("retrieval-augmented"[tiab] OR "retrieval augmented"[tiab]) AND (cancer[tiab] OR oncology[tiab]) AND (target[tiab] OR biomarker[tiab] OR gene[tiab])',
 "Q5_combinatorial_screen_BRCA_breast": '("combinatorial CRISPR"[tiab] OR "dual-guide"[tiab] OR "double knockout"[tiab] OR "paralog"[tiab] OR "genetic interaction screen"[tiab]) AND (BRCA1[tiab] OR BRCA2[tiab] OR "breast cancer"[tiab]) AND (synthetic lethal*[tiab])',
 "Q6_SL_label_validity_reproducibility": '("synthetic lethal"[tiab] OR "genetic interaction"[tiab]) AND (CRISPR[tiab]) AND (reproducibility[tiab] OR concordance[tiab] OR "scoring methods"[tiab] OR "cross-study"[tiab])',
}
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
out = {}
for k, q in Q.items():
    url = E + "esearch.fcgi?" + urllib.parse.urlencode({"db": "pubmed", "term": q, "datetype": "edat", "mindate": "2025/01/01", "maxdate": "2026/10/31", "retmax": 300, "retmode": "json"})
    r = json.loads(subprocess.run(["curl", "-sS", url], capture_output=True, text=True).stdout)
    out[k] = {"query": q, "count": int(r["esearchresult"]["count"]), "pmids": r["esearchresult"]["idlist"]}
    time.sleep(0.4)
allp = sorted({p for v in out.values() for p in v["pmids"]})
meta = {}
for i in range(0, len(allp), 150):
    ids = ",".join(allp[i:i+150])
    x = subprocess.run(["curl", "-sS", E + "esummary.fcgi?db=pubmed&retmode=json&id=" + ids], capture_output=True, text=True).stdout
    j = json.loads(x)["result"]
    for p in allp[i:i+150]:
        m = j.get(p, {})
        doi = next((a["value"] for a in m.get("articleids", []) if a["idtype"] == "doi"), None)
        meta[p] = {"title": m.get("title"), "source": m.get("source"), "pubdate": m.get("pubdate"), "epubdate": m.get("epubdate"),
                   "doi": doi, "first_author": (m.get("authors") or [{}])[0].get("name"), "pubtype": m.get("pubtype")}
    time.sleep(0.4)
json.dump({"run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "date_field": "edat", "range": "2025/01/01-2026/10/31", "queries": out, "records": meta}, open("search_2025_2026.json", "w"), indent=1)
for k, v in out.items(): print(k, v["count"], len(v["pmids"]))
print(len(allp))
