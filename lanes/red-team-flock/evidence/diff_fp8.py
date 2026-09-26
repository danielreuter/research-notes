import sys, random, hashlib, time
sys.path.insert(0,'/tmp/wtfb/backends/flock/python'); sys.path.insert(0,'/tmp/wtfb/packages/verity/src')
from verity_flock import lowering as Lw
from verity.ml.tc import models
from verity.ml.tc.silicon import tc_dot
rel='fp8-ada'
txt=Lw.netlist(rel); sha=hashlib.sha256(txt.encode()).hexdigest(); print('sha',sha,'pin',Lw.PINS.get(rel), sha==Lw.PINS.get(rel))
open('/tmp/pbin/net-fp8-ada.txt','w').write(txt)
lines=txt.splitlines(); h=lines[0].split(); useful=int(h[2]); const=int(h[3])
fwd=0; asrt=0
for i,ln in enumerate(lines[1:1+useful]):
    v=list(map(int,ln.split())); na=v[0]; a=v[1:1+na]; nb=v[1+na]; b=v[2+na:2+na+nb]
    if i<544 or i==const: continue
    refs=[j for j in a+b if j!=const]
    fwd+=any(j>i for j in refs); asrt+= i in refs
print('rows',useful,'forward',fwd,'assert rows',asrt, 'outs', h)
pipe=Lw.PIPES[rel]; model=getattr(models,pipe.model); rng=random.Random(11)
def op():
    k=rng.choice([0,0,1,2,3])
    s=rng.getrandbits(1)<<7
    if k==0: return s|rng.randint(0,0x7E)
    if k==1: return s|rng.randint(0,7)          # zero/subnormal
    if k==2: return s|rng.randint(0x70,0x7E)    # large incl max normal
    return s|rng.randint(8,0x20)
bad=0; ex=[]; N=int(sys.argv[1])
for n in range(N):
    x=[op() for _ in range(pipe.k)]; w=[op() for _ in range(pipe.k)]
    ce=rng.choice([rng.randint(1,254),0,rng.randint(200,254),rng.randint(1,30)])
    c=(rng.getrandbits(1)<<31)|(ce<<23)|rng.getrandbits(23)
    want=tc_dot(model,c,x,w)
    got,y,ok=Lw.evaluate(rel,x,w,c)
    fin=((want>>23)&0xFF)!=0xFF
    if not ok:
        if fin: bad+=1; ex.append(('unsat',hex(c),hex(want)))
        continue
    if got!=want: bad+=1; ex.append(('mismatch',hex(c),hex(want),hex(got)))
print('N',N,'bad',bad,ex[:5])
