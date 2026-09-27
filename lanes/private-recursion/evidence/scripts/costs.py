import json, os, time
from verity_flock.recursion import statement as T, vb, gadgets
ART=os.environ.get('ART','/tmp/pr/arts')
circ=T.parse_circuit(open(ART+'/d9837120/circuit.txt').read())
st=T.Statement(circ,T.load_public(ART+'/d9837120/pub-8.bin',circ),None)
fr=vb.Frame.of(st); p=vb.build(fr)
print(json.dumps({"vb_digest":p.digest(),"ands":p.ands(),"ops":len(p.ops),"io_bits":p.io_sizes(),
  "gadgets":{"sha256":gadgets.sha_ands("sha256"),"sha512":gadgets.sha_ands("sha512"),"gf128_mul":gadgets.GF_MUL_ANDS},
  "costs_depth1":p.costs(1),"costs_depth2":p.costs(2),"costs_depth3":p.costs(3),
  "C":{"a":len(st.C.a),"b":len(st.C.b),"useful":st.C.useful},"bounds":st.B.__dict__,
  "inner":{"m":fr.B.m,"rounds_per_rep":len(fr.layouts[0].rounds),"round_bytes_per_rep":sum(fr.layouts[0].round_bytes(k) for k in range(len(fr.layouts[0].rounds))),"commitments":len(fr.msg_lens)}}, indent=1))
