import sys, random, hashlib
sys.path.insert(0,'/tmp/wtfb/backends/flock/python'); sys.path.insert(0,'/tmp/wtfb/packages/verity/src')
from verity_flock import lowering as Lw, unit as U
from verity.ml.tc import models
from verity.ml.tc.cast import f32_to_bf16_word
from verity.ml.tc.silicon import tc_dot
rel=sys.argv[1]; N=int(sys.argv[2])
if rel not in Lw.PIPES:
    Lw.PIPES[rel]=Lw.Pipe("bf16-ampere", U.BF16, (8, 8), 25, -132, True, "AMPERE_BF16_M16N8K16")
txt=Lw.netlist(rel); sha=hashlib.sha256(txt.encode()).hexdigest(); print(rel,'sha',sha,'pin',Lw.PINS.get(rel))
open(f'/tmp/pbin/net-{rel}.txt','w').write(txt)
lines=txt.splitlines(); h=lines[0].split(); useful=int(h[2]); const=int(h[3])
fwd=asrt=0
for i,ln in enumerate(lines[1:1+useful]):
    v=list(map(int,ln.split())); na=v[0]; a=v[1:1+na]; nb=v[1+na]; b=v[2+na:2+na+nb]
    if i<544 or i==const: continue
    refs=[j for j in a+b if j!=const]; fwd+=any(j>i for j in refs); asrt+= i in refs
print(' header',h[:12],'rows',useful,'forward',fwd,'assert',asrt)
pipe=Lw.PIPES[rel]; model=getattr(models,pipe.model); rng=random.Random(5)
bits=pipe.word_bits
def op():
    k=rng.choice([0,0,1,2,3]); 
    if bits==16:
        s=rng.getrandbits(1)<<15
        e=[rng.randint(1,254),0,rng.randint(230,254),rng.randint(1,40)][k if k<4 else 0]
        return s|(e<<7)|rng.getrandbits(7)
    s=rng.getrandbits(1)<<7
    return s|[rng.randint(0,0x7E),rng.randint(0,7),rng.randint(0x70,0x7E),rng.randint(8,0x20)][k if k<4 else 0]
bad=0; ex=[]
for n in range(N):
    x=[op() for _ in range(pipe.k)]; w=[op() for _ in range(pipe.k)]
    ce=rng.choice([rng.randint(1,254),0,rng.randint(200,254),rng.randint(1,30)])
    c=(rng.getrandbits(1)<<31)|(ce<<23)|rng.getrandbits(23)
    want=tc_dot(model,c,x,w); got,y,ok=Lw.evaluate(rel,x,w,c); fin=((want>>23)&0xFF)!=0xFF
    if not ok:
        if fin: bad+=1; ex.append(('unsat',hex(c),hex(want)))
        continue
    if got!=want or (pipe.epilogue and y!=f32_to_bf16_word(want)): bad+=1; ex.append(('mm',hex(c),hex(want),hex(got)))
print(' N',N,'bad',bad,ex[:4])
