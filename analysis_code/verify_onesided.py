"""Two checks on the one-sided exact sign-flip test at n=5 independent components."""
import numpy as np, pandas as pd
from scipy import stats as sps
rng = np.random.default_rng(7)
n = 5
M = np.array([[1 if (k>>j)&1 else -1 for j in range(n)] for k in range(2**n)], float)
x = rng.standard_normal((200000, n))
s = x @ M.T
p1 = (s >= s[:, -1:] - 1e-12).mean(1)
allpos = (x > 0).all(1)
print("A. rejection event identical to 'all five components positive'? ",
      bool(np.array_equal(p1 <= 0.05, allpos)), " | reject rate", (p1<=0.05).mean(),
      " | 1/32 =", 1/32)
print("B. attainable one-sided p-grid at n=5:", sorted(set(np.round(np.unique(p1),5)))[:6])
print()
print("C. type I error = q^5 where q = P(component value > 0) under the null:")
for q in (0.50, 0.52, 0.5493, 0.55, 0.58, 0.60):
    print(f"     q={q:.4f} -> q^5 = {q**5:.4f} {'OK' if q**5<=0.05 else 'EXCEEDS 0.05'}")
print(f"     exact break-even q = 0.05**(1/5) = {0.05**0.2:.4f}")
print()
print("D. q measured under each simulated error law (mean-zero, component-level):")
def draw(kind, m, size):
    z = rng.standard_normal((m, size))
    if kind=="normal": return z
    if kind.startswith("gamma"):
        k=float(kind[5:]); g=rng.gamma(k,1.0,(m,size)); return (g-k)/np.sqrt(k)
    if kind=="t3": return rng.standard_t(3,(m,size))/np.sqrt(3.0)
    if kind=="chisq1": return (z**2-1)/np.sqrt(2)
    if kind=="chisq1_left": return -((z**2-1)/np.sqrt(2))
    if kind=="lognormal":
        v=np.exp(z*0.8); mm=np.exp(0.32); vv=(np.exp(0.64)-1)*np.exp(0.64); return (v-mm)/np.sqrt(vv)
    if kind=="lognormal_left":
        v=np.exp(z*0.8); mm=np.exp(0.32); vv=(np.exp(0.64)-1)*np.exp(0.64); return -((v-mm)/np.sqrt(vv))
for kind in ("normal","t3","gamma4","gamma1","lognormal","chisq1","lognormal_left","chisq1_left"):
    y = draw(kind, 200000, n)
    q = float((y>0).mean()); rate = float((y>0).all(1).mean())
    sk = float(sps.skew(y.ravel()))
    print(f"   {kind:16s} skew {sk:+7.2f}  q={q:.4f}  q^5={q**5:.4f}  measured all-positive rate={rate:.4f}"
          f"  {'OK' if rate<=0.05 else '*** EXCEEDS 0.05 ***'}")
