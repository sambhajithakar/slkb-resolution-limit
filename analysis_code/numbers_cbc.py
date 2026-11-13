"""CBC guide for authors: 'Use decimal points (not commas); use a space for
thousands (10 000 and above).' Rewrites 1,234,567 -> 1 234 567 (>=10000) or 1234 (<10000),
leaving everything else untouched. Uses a non-breaking space so the number never wraps."""
import re, sys
NB = " "
def fix(m):
    raw = m.group(0)
    digits = raw.replace(",", "")
    if len(digits) < 5:          # below 10 000: no separator at all
        return digits
    out, n = "", digits
    while len(n) > 3:
        out = NB + n[-3:] + out
        n = n[:-3]
    return n + out
src, dst = sys.argv[1], sys.argv[2]
t = open(src, encoding="utf-8").read()
t2 = re.sub(r"\b\d{1,3}(?:,\d{3})+\b", fix, t)
open(dst, "w", encoding="utf-8").write(t2)
print("thousands separators:", len(re.findall(r"\b\d{1,3}(?:,\d{3})+\b", t)), "numbers rewritten")
