import pandas as pd, json, sqlite3
OUT="/mnt/project-files/12_Q1_Manuscript_Package/02_Scientific_Results/tables/"
st = pd.read_csv("pilot/screen_table.csv")
st["study"]=st["study"].astype(str)
NAMES={"26864203":"Wong 2016","28319085":"Han 2017","28319113":"Shen 2017","29251726":"Najm 2018",
 "29452643":"Zhao 2018","30033366":"Horlbeck 2018","33637726":"Thompson 2021","33956155":"Diehl 2021",
 "34469736":"Parrish 2021","34857952":"Ito 2021","36060092":"Tang 2022"}
CRIT={"26864203":"LFC < -0.9, Q < 0.01","28319085":"SL score < -4","28319113":"SL score < -3",
 "29452643":"SL score < -3","30033366":"SL score < -3","33956155":"LFC < -1","36060092":"SL score < -0.361"}
t1 = pd.DataFrame({
 "Source study": st.study.map(NAMES), "PMID": st.study, "Cell model": st.cell_line,
 "Published SL criterion": st.study.map(CRIT),
 "Queries (anchor genes)": st.n_queries_all,
 "Queries with >=1 positive": st.n_queries,
 "Mean candidates per query": st.mean_candidates.round(1),
 "Published SL call rate (%)": (st.prevalence*100).round(2)})
t1 = t1.sort_values(["Source study","Cell model"])
t1.to_csv(OUT+"Table_1_eligible_screens.csv", index=False)

con = sqlite3.connect("slkb/SLKB.db")
q = lambda s: con.execute(s).fetchone()[0]
rows=[]
rows.append(("Deposited rows in cdko_original_sl_results", f"{q('select count(*) from cdko_original_sl_results'):,}",
             "every deposited screened gene pair, all 11 source studies"))
rows.append(("Distinct values of SL_or_not", "2 ('SL', 'Not SL')", "0 NULLs; verified across all deposited rows"))
rows.append(("Rows with a missing gene symbol", str(q("select count(*) from cdko_original_sl_results where gene_1 is null or gene_2 is null or trim(gene_1)='' or trim(gene_2)=''")), "none"))
rows.append(("Self-pairs (gene_1 = gene_2)", str(q("select count(*) from cdko_original_sl_results where gene_1=gene_2")), "none"))
n_coll = q("select count(*) from (select gene_pair_id from cdko_original_sl_results group by gene_pair_id having count(distinct study_origin)>1)")
rows.append(("gene_pair_id values shared by two or more source studies", f"{n_coll:,}",
             "a join on gene_pair_id alone can attach one study's score to another study's pair"))
rows.append(("Distinct gene_pair_id values carrying a GEMINI score", f"{q('select count(distinct gene_pair_id) from gemini_score'):,}",
             "score coverage is partial and study-dependent"))
rows.append(("Source study with no deposited score of its own", "Han 2017 (PMID 28319085), 20,791 rows",
             "all of its rows are unscored in the deposited score tables"))
rows.append(("Cell model excluded as a true published zero", "786-O (Najm 2018)",
             "no significant SL pair published for it; SLKB's own table misprints the name as '876O'"))
rows.append(("Span of published SL call rates across the 11 eligible screens",
             f"{st.prevalence.min()*100:.2f}% to {st.prevalence.max()*100:.2f}%",
             "Han/K562 lowest; Diehl/RPE1 highest - the label is not uniform across clusters"))
rows.append(("Label-generating publications excluded from every corpus snapshot", "11 of 11",
             "every deposited study_origin PMID is on the exclusion list and every PMID on that list is one of the 11"))
t2 = pd.DataFrame(rows, columns=["Property of the deposited resource","Value","Consequence for a benchmark built on it"])
t2.to_csv(OUT+"Table_2_resource_audit.csv", index=False)

r = pd.read_csv("analysis/exchangeability_results.csv")
ind = r[(~r.heteroscedastic)&(r.rho_within_study==0)&(r.rho_shared_line==0)]
SK={"normal":"0 (normal)","t3":"0 (t3, heavy-tailed)","gamma16":"0.5 (gamma)","gamma4":"1.0 (gamma)",
    "gamma1":"2.0 (exponential)","chisq1":"2.8 (chi-square, 1 df)","lognormal":"2.9 (lognormal)"}
mx = r.groupby("errors")[["size_cell_two_sided","size_study_two_sided","size_conjunction_two_sided","size_cell_paired_t_two_sided"]].max()
t3 = pd.DataFrame({
 "Error law of the cluster values (skewness)": [SK[e] for e in ind.errors],
 "Cell-model arm, at independence": ind.size_cell_two_sided.values,
 "Study arm, at independence": ind.size_study_two_sided.values,
 "Conjunction, at independence": ind.size_conjunction_two_sided.values,
 "Paired t (cell-model), at independence": ind.size_cell_paired_t_two_sided.values,
 "Cell-model arm, worst over the dependence grid": [mx.loc[e,"size_cell_two_sided"] for e in ind.errors],
 "Conjunction, worst over the dependence grid": [mx.loc[e,"size_conjunction_two_sided"] for e in ind.errors],
}).round(4)
order=["normal","t3","gamma16","gamma4","gamma1","chisq1","lognormal"]
t3["_o"]=[order.index(e) for e in ind.errors]; t3=t3.sort_values("_o").drop(columns="_o")
t3.to_csv(OUT+"Table_3_measured_type_I_error.csv", index=False)
for n,d in (("Table_1_eligible_screens",t1),("Table_2_resource_audit",t2),("Table_3_measured_type_I_error",t3)):
    print("==",n); print(d.to_string(index=False)[:1800]); print()
