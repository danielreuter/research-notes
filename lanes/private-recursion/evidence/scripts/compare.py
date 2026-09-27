import csv, json, sys
rec = {r['session']: r for r in csv.DictReader(open('/tmp/pr/arts/78ef0a6e/agreement.tsv'), delimiter='\t')}
rows = [json.loads(l) for l in open('/tmp/pr/ev/differential.jsonl')]
for m in json.load(open('/tmp/pr/mut/retain/retained.json')):
    if m['name'] not in rec:
        e = m['expect']
        rec[m['name']] = {'lean': 'A' if e['accepted'] else 'R', 'upstream': 'A' if e.get('upstream_accepted', e['accepted']) else 'R'}
out = open('/tmp/pr/ev/differential.tsv', 'w')
out.write('session\tlean\tupstream\tvb\tagree_lean\tvb_why\n')
agree = 0
for r in rows:
    x = rec[r['session']]
    ok = x['lean'] == r['vb']; agree += ok
    out.write(f"{r['session']}\t{x['lean']}\t{x['upstream']}\t{r['vb']}\t{'yes' if ok else 'NO'}\t{r['why']}\n")
print(f'{agree}/{len(rows)} agree with Lean')
