import time, sys, json, os, numpy as np
ART=os.environ.get('ART','/tmp/pr/arts')
from pathlib import Path
from verity_flock.recursion import session as S, statement as T, vb, coins, witness as W, program as P
circ=T.parse_circuit(open(ART+'/d9837120/circuit.txt').read())
pub=T.load_public(ART+'/d9837120/pub-8.bin', circ)
st=T.Statement(circ,pub,T.load_comp(ART+'/04259cdd/comp.rows'))
fr=vb.Frame.of(st); prog=vb.build(fr)
dirs=sys.argv[1:]
for d in dirs:
    t=time.time()
    try:
        sess=S.load_session(d)
        tabs=coins.tables(fr,st,sess)
        pubi,wit=W.convert(fr,st,st.C,pub,sess,tabs,rng=np.random.default_rng(7))
        r=P.evaluate(prog,{**tabs,**pubi,**wit})
        verdict='A' if r.accepted else 'R'; why='; '.join(f'{w} x{n}' for w,n in r.failed)
    except W.Refused as e:
        verdict='R'; why='refused: '+str(e)
    print(json.dumps({'session':Path(d).name,'vb':verdict,'why':why,'s':round(time.time()-t,1)}), flush=True)
