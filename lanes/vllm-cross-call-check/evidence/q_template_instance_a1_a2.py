"""PR #131: core's Q_template_instance v0 builds and evaluates one-stage's A1/A2 objects (population_program at 761c4402) identically.
Result 07:31Z: A2 N=183680 digest 17478e8544cf132f.. 183680 units verify ok; A1 N=1024 digest ba90a2941aede907.. 1024 units."""
from verity.ir import partition_object as PO
from verity_numerical.bench import templates as T
from verity_one_stage import partition as P
rope = T.subcircuit("rope-head", D=64).definition()
for n in (183680, 1024):
    prog = P.population_program(rope, n)
    obj = PO.build(prog, PO.template_instance_query(rope))
    assert obj == P.partition(prog, P.template_instance_query(rope.id))
    print(n, PO.digest(obj), PO.evaluate(prog, obj["query"]).population, PO.verify(obj, prog).ok)
