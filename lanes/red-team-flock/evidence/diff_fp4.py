import sys, random, hashlib, time
sys.path.insert(0,'/tmp/wtfb/backends/flock/python'); sys.path.insert(0,'/tmp/wtfb/packages/verity/src')
from verity_flock import lowering as Lw
from verity.ml.tc import models
M=models.BLACKWELL_SM120_NVF4
for r in ("bf16-hopper","fp8-ada","fp8-hopper"):
    assert hashlib.sha256(Lw.netlist(r).encode()).hexdigest()==Lw.PINS[r], r
txt=Lw.netlist("fp4-nvf4"); sha=hashlib.sha256(txt.encode()).hexdigest(); print('fp4 sha',sha, sha.startswith('fb52a87c01a8a41f'))
open('/tmp/pbin/net-fp4-nvf4.txt','w').write(txt)
L=txt.splitlines(); h=L[0].split(); useful=int(h[2]); const=int(h[3]); nin=int(h[4])
fwd=asrt=0; badin=0
for i,ln in enumerate(L[1:1+useful]):
    v=list(map(int,ln.split())); na=v[0]; a=v[1:1+na]; nb=v[1+na]; b=v[2+na:2+na+nb]
    if i<nin:
        badin += not (a==[i] and b==[i]); continue
    if i==const: continue
    refs=[j for j in a+b if j!=const]; fwd+=any(j>i for j in refs); asrt+= i in refs
print('header',h[:14],'rows',useful,'n_in',nin,'bad input rows',badin,'forward',fwd,'assert',asrt)
rng=random.Random(int(sys.argv[2]) if len(sys.argv)>2 else 3)
def scale(kind):
    if kind==0: return rng.randint(1,0x7E)           # normal/subnormal, valid
    if kind==1: return rng.randint(0,7)              # zero/subnormal mantissa
    if kind==2: return rng.randint(0x70,0x7E)        # top exponents
    if kind==3: return rng.choice([0x00,0x08,0x10])  # zero mantissa cases
    return rng.randint(0,0x7E)
def acc():
    k=rng.randint(0,5); s=rng.getrandbits(1)<<31
    if k==0: return s
    if k==1: return s|rng.getrandbits(23)
    if k==2: return s|(rng.randint(200,254)<<23)|rng.getrandbits(23)
    if k==3: return s|(rng.randint(1,40)<<23)|rng.getrandbits(23)
    return s|(rng.randint(1,254)<<23)|rng.getrandbits(23)
N=int(sys.argv[1]); bad=0; unsat_ok=0; ex=[]
t=time.time()
for n in range(N):
    sparse=rng.random()<0.3
    x=[0 if (sparse and rng.random()<0.8) else rng.randint(0,15) for _ in range(64)]
    w=[0 if (sparse and rng.random()<0.8) else rng.randint(0,15) for _ in range(64)]
    if rng.random()<0.1:  # cancelling group: w group negated copy of x pattern
        g=rng.randint(0,3); 
        for i in range(16*g,16*g+8): w[i]=x[i]; w[i+8]=x[i+8]^8 if x[i+8]==x[i] else w[i+8]
    sx=[scale(rng.randint(0,4)) for _ in range(4)]; sw=[scale(rng.randint(0,4)) for _ in range(4)]
    c=acc()
    want=M.step_scaled(c,x,w,sx,sw)
    got,_,ok=Lw.evaluate("fp4-nvf4",x,w,c,sx,sw)
    fin=((want>>23)&0xFF)!=0xFF
    if not ok:
        if fin: bad+=1; ex.append(('unsat',x[:4],sx,sw,hex(c),hex(want)))
        else: unsat_ok+=1
        continue
    if got!=want: bad+=1; ex.append(('mm',sx,sw,hex(c),hex(want),hex(got)))
# invalid scales must be unsat
inv=0
for sv in (0x7F,0xFF,0x80):
    got,_,ok=Lw.evaluate("fp4-nvf4",[1]*64,[1]*64,0,[sv,1,1,1],[1,1,1,1]); inv+= (not ok)
print('N',N,'bad',bad,'unsat(nonfinite ref)',unsat_ok,'invalid-scale unsat',inv,'/3', ex[:3], '%.0fs'%(time.time()-t))
