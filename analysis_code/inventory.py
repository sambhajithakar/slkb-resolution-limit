import csv, sys, collections
path = "/mnt/project-files/uploads/SLKB_2026-10-28/SLKB_calculated_scores.csv"
pairs = collections.Counter()
genes = collections.defaultdict(set)
with open(path, newline="") as fh:
    r = csv.DictReader(fh)
    for row in r:
        s = (row["study_origin"] or "").strip()
        c = (row["cell_line_origin"] or "").strip()
        pairs[(s, c)] += 1
        genes[(s, c)].add(row["gene_1"]); genes[(s, c)].add(row["gene_2"])
print("n_screens(study,cell):", len(pairs))
print("n_studies:", len({s for s, c in pairs}))
print("n_cell_lines:", len({c for s, c in pairs}))
print()
print(f"{'study':<12}{'cell':<14}{'obs':>10}{'genes':>8}")
for (s, c), n in sorted(pairs.items()):
    print(f"{s:<12}{c:<14}{n:>10}{len(genes[(s,c)]):>8}")
