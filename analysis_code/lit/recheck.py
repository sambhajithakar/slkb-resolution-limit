import json, sys, time, urllib.request, xml.etree.ElementTree as ET
recs=json.load(open("lit/verified_refs_2026-10-31.json"))
if isinstance(recs,dict): recs=recs.get("records",recs)
pmids=[r["pmid"] for r in (recs.values() if isinstance(recs,dict) else recs)]
print("records:",len(pmids))
out={}
for i in range(0,len(pmids),20):
    chunk=pmids[i:i+20]
    url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="+",".join(chunk)
    x=ET.fromstring(urllib.request.urlopen(url,timeout=60).read())
    for a in x.findall(".//PubmedArticle"):
        p=a.findtext(".//MedlineCitation/PMID")
        t=(a.findtext(".//ArticleTitle") or "").strip()
        out[p]=t
    time.sleep(0.4)
json.dump(out,open("lit/recheck_2026-11-03.json","w"),indent=1)
missing=[p for p in pmids if p not in out]
print("resolved:",len(out),"missing:",missing)
