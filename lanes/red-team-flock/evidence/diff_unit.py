import sys, random, hashlib, time
sys.path.insert(0,'/tmp/fb/backends/flock/python'); sys.path.insert(0,'/tmp/fb/packages/verity/src')
from verity_flock import lowering as Lw
from verity.ml.tc import models
from verity.ml.tc.cast import f32_to_bf16_word
from verity.ml.tc.silicon import tc_dot
rel='bf16-hopper'
t=time.time(); txt=Lw.netlist(rel); print('netlist sha', hashlib.sha256(txt.encode()).hexdigest()==Lw.PINS[rel], 'gen %.1fs'%(time.time()-t))
lines=txt.splitlines(); h=lines[0].split(); useful=int(h[2]); const=int(h[3])
bad_topo=0; asserts=0
for i,ln in enumerate(lines[1:1+useful]):
    v=list(map(int,ln.split())); na=v[0]; a=v[1:1+na]; nb=v[1+na]; b=v[2+na:2+na+nb]
    if i<544 or i==const: continue
    refs=[j for j in a+b if j!=const]
    if any(j>i for j in refs): bad_topo+=1
    if i in refs: asserts+=1
print('rows',useful,'forward refs',bad_topo,'self-referencing (assert) rows',asserts)
pipe=Lw.PIPES[rel]; model=getattr(models,pipe.model); rng=random.Random(7)
def op(kind):
    s=rng.getrandbits(1)<<15
    if kind==0: return s|(rng.randint(1,254)<<7)|rng.getrandbits(7)
    if kind==1: return s|rng.getrandbits(7)            # zero/subnormal
    if kind==2: return s|(rng.randint(230,254)<<7)|rng.getrandbits(7)
    return s|(rng.randint(1,40)<<7)|rng.getrandbits(7)
N=int(sys.argv[1]) if len(sys.argv)>1 else 300
bad=0; skipped=0; ex=[]
for n in range(N):
    kinds=[rng.choice([0,0,1,2,3]) for _ in range(2*pipe.k)]
    x=[op(k) for k in kinds[:pipe.k]]; w=[op(k) for k in kinds[pipe.k:]]
    ce=rng.choice([rng.randint(1,254),0,rng.randint(200,254),rng.randint(1,30)])
    c=(rng.getrandbits(1)<<31)|(ce<<23)|rng.getrandbits(23)
    try: want=tc_dot(model,c,x,w)
    except Exception as e: skipped+=1; continue
    got,y,ok=Lw.evaluate(rel,x,w,c)
    fin = ((want>>23)&0xFF)!=0xFF
    if not ok:
        if fin: bad+=1; ex.append(('unsat-but-finite',hex(c),hex(want)))
        continue
    if got!=want or (y is not None and y!=f32_to_bf16_word(want)):
        bad+=1; ex.append(('mismatch',hex(c),hex(want),hex(got)))
print('N',N,'bad',bad,'skipped',skipped, ex[:5])
