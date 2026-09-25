// red-team-flock third audit (flock-link @ 4b560b2b): appended to a copy of backends/flock/live/src/bin/flock-link.rs
// (everything from `fn main()` on is replaced) and built as crates/flock-live/examples/rtf_link_attacks.rs.
// Output: one `RTF\t{json}` line per attack.

struct Mitm {
    inner: InProc,
    f: Box<dyn FnMut(Req) -> Vec<Req> + Send>,
}

impl Transport for Mitm {
    fn call(&mut self, req: Req) -> Result<Resp, String> {
        let want = req.encode()[0];
        let mut last = Ok(Resp::Ok);
        let mut back = None;
        let reqs = (self.f)(req);
        if reqs.is_empty() {
            return Ok(Resp::Ok);
        }
        for r in reqs {
            let same = r.encode()[0] == want;
            last = self.inner.call(r);
            if same {
                back = Some(last.clone());
            }
        }
        back.unwrap_or(last)
    }
}

fn report(name: &str, cond: &str, expect: &str, v: &Value, rec: &Value) {
    let acc = v["accepted"].as_bool().unwrap_or(false);
    let pass = match expect { "reject" => !acc, "accept" => acc, _ => true };
    println!("RTF\t{}", json!({"attack": name, "cond": cond, "expect": expect, "accepted": acc, "pass": pass,
        "why": v["why"], "prover_stopped": v["prover_stopped"], "link_mode": rec["link_mode"],
        "require_link": rec["config"]["require_link"], "link_sha256_set": !rec["link_sha256"].is_null()}));
}

fn attack(ch: &Arc<Chain>, name: &str, cond: &str, expect: &str, require_link: bool, plan: &Plan,
          f: impl FnMut(Req) -> Vec<Req> + Send + 'static) {
    let (st, _, _) = instance(ch, 0xA, plan);
    let s = Arc::new(Mutex::new(server(ch, leaf_digests(ch, &st))));
    s.lock().unwrap().cfg.require_link = require_link;
    let t = shared(Mitm { inner: InProc(s.clone()), f: Box::new(f) });
    let (v, _) = session(ch, t, 0xA, plan);
    let rec = s.lock().unwrap().record_json();
    report(name, cond, expect, &v, &rec);
}

fn attacks(ch: Arc<Chain>) {
    let h = Plan::honest;
    let leaf_bytes = 32 * ch.chunks;

    // L1: an exchange-mode verifier configured without the R5 gate. y is withheld (the prover is told Ok) and sent
    // only just before Finish, so every Flock coin is issued before y exists.
    for gate in [false, true] {
        let held: Arc<Mutex<Option<Req>>> = Arc::new(Mutex::new(None));
        let hh = held.clone();
        attack(&ch, &format!("y_sent_after_all_flock_coins_require_link_{gate}"), "L1/R5", if gate { "reject" } else { "any" },
               gate, &h(), move |req| match req {
                   Req::Link(b) => { *hh.lock().unwrap() = Some(Req::Link(b)); vec![] }
                   Req::Finish => { let mut v: Vec<Req> = hh.lock().unwrap().take().into_iter().collect(); v.push(Req::Finish); v }
                   r => vec![r],
               });
    }

    // L2: the two y values swapped on the wire (each is a correct evaluation, at the other point).
    attack(&ch, "y1_y2_swapped", "L2", "reject", true, &h(), |req| match req {
        Req::Link(b) => { let mut c = b[16..32].to_vec(); c.extend_from_slice(&b[..16]); vec![Req::Link(c)] }
        r => vec![r],
    });
    // L2: y replaced by the evaluation of z with the linked bits of one leaf zeroed (a different b of the right shape).
    attack(&ch, "y_of_other_operands", "L2", "reject", true, &h(), |req| match req {
        Req::Link(mut b) => { b[5] ^= 0x40; b[16 + 9] ^= 0x02; vec![Req::Link(b)] }
        r => vec![r],
    });

    // L1/L3: Commit carrying an extra table, or a root_B for a table name outside the statement.
    attack(&ch, "commit_extra_table", "L1/L3", "reject", true, &h(), |req| match req {
        Req::Commit { root_f, mut roots, publics } => { roots.push(("chain9".into(), vec![1u8; 32])); vec![Req::Commit { root_f, roots, publics }] }
        r => vec![r],
    });
    // L1: Commit sent before Hello (Hello dropped, prover told Ok).
    attack(&ch, "commit_before_hello", "L1/R7", "reject", true, &h(), |req| match req {
        Req::Hello(_) => vec![],
        r => vec![r],
    });

    // L4: the committed public chunk values of leaves 0 and 1 swapped (each a genuine chunk chain of some leaf).
    attack(&ch, "commit_publics_leaves_swapped", "L4", "reject", true, &h(), move |req| match req {
        Req::Commit { root_f, roots, mut publics } => {
            let p = &mut publics[0].1;
            let (a, b) = p.split_at_mut(leaf_bytes);
            a.swap_with_slice(&mut b[..leaf_bytes]);
            vec![Req::Commit { root_f, roots, publics }]
        }
        r => vec![r],
    });
    // L4: public words committed honestly, but the chunk outputs the proof binds are those of a flipped chunk value
    // (publics digest in the binding round differs from the committed, checked one).
    attack(&ch, "proof_binds_other_publics", "L4/C4", "reject", true, &Plan { publics_flip: true, ..h() }, |r| vec![r]);
    // L1: rep 1's binding round names a different root than the committed root_B (other witness).
    attack(&ch, "rep1_other_witness", "L1/R1", "reject", true, &Plan { rep1_other_witness: true, ..h() }, |r| vec![r]);
    // Honest control through the same MITM plumbing.
    attack(&ch, "honest_control", "-", "accept", true, &h(), |r| vec![r]);
}

fn main() {
    let vus: usize = arg("--vus", "8").parse().unwrap();
    let k: usize = arg("--k", "1536").parse().unwrap();
    attacks(Arc::new(Chain::new(vus, k)));
}
