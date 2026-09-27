"""Swap test (spec I.9): two different circuits with the same bounds give the same V[B] and the same public artifact shapes."""
import json, re, os
ART=os.environ.get('ART','/tmp/pr/arts')
import numpy as np
from verity_flock.recursion import statement as T, vb
text = open(ART+'/d9837120/circuit.txt').read()
pub_path = ART+'/d9837120/pub-8.bin'
comp = T.load_comp(ART+'/04259cdd/comp.rows')

def variant(text):
    lines = text.split('\n')
    meta = json.loads(lines[1][5:])
    meta['leaves_in'] = [[2 * (u % 16) + 32 * (u // 16), 2 * (u % 16) + 1 + 32 * (u // 16), 64 + 2 * (u % 16) + 32 * (u // 16),
                          65 + 2 * (u % 16) + 32 * (u // 16)] for u in range(32)]
    meta['leaves_out'] = [[2 * (u % 16) + 32 * (u // 16), 2 * (u % 16) + 1 + 32 * (u // 16)] for u in range(32)]
    lines[1] = 'META ' + json.dumps(meta, separators=(',', ':'))
    # a different unit: drop the last XOR term of every B row that has at least three terms (another function)
    head = lines[3].split(); useful = int(head[2])
    for i in range(useful):
        v = list(map(int, lines[4 + i].split())); na = v[0]; a = v[1:1 + na]; b = v[2 + na:]
        if len(b) >= 3 and i != useful - 1:
            b = b[:-1]
        lines[4 + i] = ' '.join(map(str, [na] + a + [len(b)] + b))
    return '\n'.join(lines)

out = []
for name, t in (("rope-head/neox (the recorded circuit)", text), ("a different unit, gptj leaf maps", variant(text))):
    circ = T.parse_circuit(t)
    st = T.Statement(circ, T.load_public(pub_path, circ), comp)
    fr = vb.Frame.of(st)
    p = vb.build(fr)
    out.append(dict(circuit=name, C_entries=[len(st.C.a), len(st.C.b)], leaves_in_0=st.C.leaves_in[0], vb_digest=p.digest(),
                    vb_ands=p.ands(), vb_ops=len(p.ops), inner_commitments=[len(fr.msg_lens), 64], committed_bytes=sum(fr.msg_lens),
                    outer_public_bits=p.io_sizes()['public'], outer_witness_input_bits=p.io_sizes()['witness'],
                    enc_bits=sum(int(np.prod(s)) for _, s in fr.enc_fields())))
for o in out: print(json.dumps(o))
same = all(out[0][k] == out[1][k] for k in ('vb_digest', 'vb_ands', 'inner_commitments', 'committed_bytes', 'outer_public_bits', 'outer_witness_input_bits', 'enc_bits'))
print('C differ:', out[0]['C_entries'] != out[1]['C_entries'] and out[0]['leaves_in_0'] != out[1]['leaves_in_0'], ' public artifacts identical:', same)
