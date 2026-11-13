import sys, json
sys.path.insert(0, "/mnt/project-files/06_Implementation")
from brca_rag import labels
ELIG = {("26864203","OVCAR8"),("28319085","K562"),("28319113","293T"),("28319113","A549"),("28319113","HELA"),
        ("29452643","A549"),("29452643","HELA"),("30033366","JURKAT"),("30033366","K562"),("33956155","RPE1"),("36060092","22RV1")}
qs = labels.load_published_calls_from_sqlite(sys.argv[1])
f = qs.frame
e = f[[(s, c) in ELIG for s, c in zip(f.study, f.cell_line)]]
q = e.groupby(["study", "cell_line", "anchor_gene"]).agg(n_cand=("relevant", "size"), n_pos=("relevant", "sum")).reset_index()
t = q.groupby(["study", "cell_line"]).agg(n_queries_all=("anchor_gene", "size"), n_queries=("n_pos", lambda x: int((x > 0).sum())),
     mean_candidates=("n_cand", "mean"), positives_directed=("n_pos", "sum")).reset_index()
t["prevalence"] = t.positives_directed / e.groupby(["study","cell_line"]).size().values
print(t.to_string()); print(t[["n_queries_all","n_queries","positives_directed"]].sum())
t.to_csv("screen_table.csv", index=False)
