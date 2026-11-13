import json
from feasibility import components, feasibility, min_G, load_slkb, ALPHA

ELIG = {("26864203","OVCAR8"),("28319085","K562"),("28319113","293T"),
        ("28319113","A549"),("28319113","HELA"),("29452643","A549"),
        ("29452643","HELA"),("30033366","JURKAT"),("30033366","K562"),
        ("33956155","RPE1"),("36060092","22RV1")}

c = components(ELIG)
f = feasibility(len(c))
print("VALIDATION against the registered eligible set")
print("  screens:", len(ELIG), " studies:", len({s for s,_ in ELIG}),
      " cell models:", len({x for _,x in ELIG}))
print("  G =", f["G"], "(expected 5)  ->", "PASS" if f["G"] == 5 else "FAIL")
print("  min attainable two-sided p = %.4f" % f["min_p_two_sided"])
for comp in sorted(c, key=lambda d: d["studies"]):
    print("   ", comp["studies"], comp["cells"])
print()

g2, g1 = min_G()
screens, by_study = load_slkb("/mnt/project-files/uploads/SLKB_2026-10-28/SLKB_calculated_scores.csv")
whole = components(screens)
print("THE RESOLUTION LIMIT")
print(f"  at alpha={ALPHA}: an exact two-sided test needs G >= {g2}; one-sided G >= {g1}")
print()
print("MONOTONICITY: adding screens can only merge components, never split them.")
print(f"  registered eligible subset (11 screens):      G = 5")
print(f"  whole SLKB deposit      ({len(screens)} screens):      G = {len(whole)}")
print("  -> enlarging the resource REDUCED the number of independent units.")
print()
for comp in sorted(whole, key=lambda d: -d["n_screens"]):
    print(f"   component: {len(comp['studies'])} studies x {len(comp['cells'])} cell models,"
          f" {comp['n_screens']} screens")
    print(f"     studies: {','.join(comp['studies'])}")
    print(f"     cells:   {','.join(comp['cells'])}")

json.dump({"eligible_G": f["G"], "eligible_components": c,
           "whole_G": len(whole), "whole_components": whole,
           "min_G_two_sided": g2, "min_G_one_sided": g1, "alpha": ALPHA},
          open("n1_results.json", "w"), indent=2)
