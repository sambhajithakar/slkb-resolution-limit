import json, subprocess, urllib.parse, time, xml.etree.ElementTree as ET

PMIDS = {
 "slkb":"37889037","ajmal":"41018953","chang":"42026135","martin":"42685085","billmann_cell":"42049019",
 "feng_corr":"39948334","musl":"42213569","seale":"35876858","noh":"42264143","bernett":"38446741",
 "yilmaz":"40493194","zietz":"38323677","bonner":"35880623","stoeger":"30226837","neeley":"40666130",
 "li_mem":"42315854","slmerk":"41337148","jun":"41544626","lai":"40293950","zarfati":"40068371",
 "shao":"41375077","wu_source":"40240349","medea":"41648610","tepeli":"38113447",
 "wong":"26864203","han":"28319085","shen":"28319113","najm":"29251726","zhao":"29452643",
 "horlbeck":"30033366","thompson":"33637726","diehl":"33956155","parrish":"34469736",
 "ito":"34857952","tang":"36060092",
}
ids = ",".join(sorted(set(PMIDS.values())))
xml = subprocess.run(["curl","-sS","--max-time","60",
  f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id={ids}"],
  capture_output=True, text=True).stdout
root = ET.fromstring(xml)
rec = {}
for a in root.findall(".//PubmedArticle"):
    pmid = a.findtext(".//MedlineCitation/PMID")
    art = a.find(".//Article")
    authors = []
    for au in a.findall(".//AuthorList/Author"):
        ln, ini = au.findtext("LastName"), au.findtext("Initials")
        if ln: authors.append(f"{ln} {ini or ''}".strip())
    j = art.findtext("./Journal/ISOAbbreviation") or art.findtext("./Journal/Title")
    y = a.findtext(".//JournalIssue/PubDate/Year") or (a.findtext(".//JournalIssue/PubDate/MedlineDate") or "")[:4]
    vol = a.findtext(".//JournalIssue/Volume"); iss = a.findtext(".//JournalIssue/Issue")
    pg = art.findtext("./Pagination/MedlinePgn") or art.findtext("./ELocationID")
    doi = next((x.text for x in a.findall(".//ArticleIdList/ArticleId") if x.get("IdType")=="doi"), None)
    rec[pmid] = dict(pmid=pmid, authors=authors, title="".join(art.find("./ArticleTitle").itertext()),
                     journal=j, year=y, volume=vol, issue=iss, pages=pg, doi=doi)
missing = [p for p in set(PMIDS.values()) if p not in rec]
print("fetched", len(rec), "missing", missing)
json.dump({"fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "key_to_pmid": PMIDS,
           "records": rec}, open("verified_refs_2026-10-31.json","w"), indent=1)
for k,p in sorted(PMIDS.items()):
    r = rec.get(p)
    if r: print(f"{k:14s} {p} | {r['authors'][0] if r['authors'] else '?'} et al. {r['journal']} {r['year']};{r['volume'] or ''} | doi {r['doi']}")
