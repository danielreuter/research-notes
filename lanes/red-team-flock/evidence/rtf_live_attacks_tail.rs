// red-team-flock re-audit of flock-live a43f6254: appended to a copy of backends/flock/live/src/bin/flock-live.rs
// (everything from `fn main()` on is replaced by this file) and built as crates/flock-live/examples/rtf_live_attacks.rs.
// Output: one `RTF\t{json}` line per attack.

/// A man-in-the-middle prover transport: `f` rewrites each request into the requests actually sent; the prover sees
/// the response to the last sent request of the original request's kind.
struct Mitm {
    inner: InProc,
    f: Box<dyn FnMut(Req) -> Vec<Req> + Send>,
    issued: Arc<Mutex<Vec<String>>>,
}

impl Transport for Mitm {
    fn call(&mut self, req: Req) -> Result<Resp, String> {
        let want = req.encode()[0];
        let mut last = Ok(Resp::Ok);
        let mut back = None;
        for r in (self.f)(req) {
            let same = r.encode()[0] == want;
            let tag = match &r {
                Req::Round { stream, n, .. } => format!("round {stream} n={n}"),
                Req::Open { stream, at, .. } => format!("open {stream} at={at}"),
                _ => String::new(),
            };
            last = self.inner.call(r);
            if same {
                back = Some(last.clone());
            }
            if !tag.is_empty() {
                self.issued.lock().unwrap().push(format!("{tag} -> {}", match &last {
                    Ok(Resp::Coins(c)) => format!("{} coins", c.len()),
                    Ok(Resp::Refused(e)) => format!("refused: {}", e.chars().take(100).collect::<String>()),
                    o => format!("{o:?}").chars().take(60).collect(),
                }));
            }
        }
        back.unwrap_or(last)
    }
}

fn mitm(st: &Arc<Stmt>, require_link: bool, f: impl FnMut(Req) -> Vec<Req> + Send + 'static)
        -> (SharedTransport, Arc<Mutex<Server>>, Arc<Mutex<Vec<String>>>) {
    let s = Arc::new(Mutex::new(server(st, require_link)));
    let issued = Arc::new(Mutex::new(Vec::new()));
    (shared(Mitm { inner: InProc(s.clone()), f: Box::new(f), issued: issued.clone() }), s, issued)
}

fn report(name: &str, cond: &str, expect: &str, v: &Value, extra: Value) {
    let acc = v["accepted"].as_bool().unwrap_or(false);
    let pass = match expect { "reject" => !acc, "accept" => acc, _ => true };
    println!("RTF\t{}", json!({"attack": name, "cond": cond, "expect": expect, "accepted": acc, "pass": pass,
        "why": v["why"], "prover_stopped": v["prover_stopped"], "extra": extra}));
}

fn swap_domain(content: &[u8], from: &[u8], to: &[u8]) -> Vec<u8> {
    let f = frame_domain(from);
    let t = frame_domain(to);
    assert!(content.starts_with(&f) && f.len() == t.len());
    let mut c = t;
    c.extend_from_slice(&content[f.len()..]);
    c
}

fn attacks(st: Arc<Stmt>) {
    let h = Plan::honest;

    // R1-a: rep 1 claims rep 0's root in its live binding round (so the server issues rep-1 coins) but proves witness B.
    {
        let rep0_first: Arc<Mutex<Option<Vec<u8>>>> = Arc::new(Mutex::new(None));
        let r0 = rep0_first.clone();
        let (t, _s, issued) = mitm(&st, true, move |req| match req {
            Req::Round { stream, content, n } if stream == "blake3/rep0" && r0.lock().unwrap().is_none() => {
                *r0.lock().unwrap() = Some(content.clone());
                vec![Req::Round { stream, content, n }]
            }
            Req::Round { stream, content: _, n } if stream == "blake3/rep1" && r0.lock().unwrap().is_some() => {
                let c = r0.lock().unwrap().take().unwrap();
                vec![Req::Round { stream, content: swap_domain(&c, &domain(0), &domain(1)), n }]
            }
            r => vec![r],
        });
        let v = session(&st, t, &Plan { witness: vec![0xA, 0xB], ..h() });
        let rep1_coins = issued.lock().unwrap().iter().filter(|l| l.starts_with("round blake3/rep1 ") && l.contains("coins")).count();
        report("rep1_claims_rep0_root_but_proves_other_witness", "R1", "reject", &v, json!({"rep1_rounds_with_coins": rep1_coins}));
    }

    // R1-b / R3: a child stream of rep 1 opened at parent position 0 (before rep 1's binding round) gets coins.
    {
        let ren = |s: String| if s == "blake3/rep1/f0" { "blake3/rep1/f1".to_string() } else { s };
        let (t, _s, issued) = mitm(&st, true, move |req| match req {
            Req::Open { stream, parent, label, at } if stream == "blake3/rep1/f0" =>
                vec![Req::Open { stream: ren(stream), parent, label, at }],
            Req::Round { stream, content, n } if stream == "blake3/rep1/f0" =>
                vec![Req::Round { stream: ren(stream), content, n }],
            Req::Open { stream, parent, label, at } if stream == "blake3/rep1" => vec![
                Req::Open { stream: stream.clone(), parent, label, at },
                Req::Open { stream: "blake3/rep1/f0".into(), parent: stream, label: b"flock-par-assist-v1".to_vec(), at: 0 },
                Req::Round { stream: "blake3/rep1/f0".into(), content: frame_domain(b"flock-par-assist-v1"), n: 2 },
                Req::Round { stream: "blake3/rep1/f0".into(), content: vec![0u8; 16], n: 2 },
            ],
            r => vec![r],
        });
        let v = session(&st, t, &h());
        let pre = issued.lock().unwrap().iter().filter(|l| l.starts_with("round blake3/rep1/f0")).cloned().collect::<Vec<_>>();
        report("child_of_rep1_opened_before_rep1_root", "R1/R3", "reject", &v, json!({"child_rounds_before_root": pre}));
    }

    // R3: fork child opened at a claimed parent position one off.
    {
        let (t, _s, _i) = mitm(&st, true, move |req| match req {
            Req::Open { stream, parent, label, at } if !parent.is_empty() && stream == "blake3/rep0/f0" =>
                vec![Req::Open { stream, parent, label, at: at + 1 }],
            r => vec![r],
        });
        report("fork_child_at_wrong_parent_position", "R3", "reject", &session(&st, t, &h()), json!({}));
    }

    // R3: the fork child's first round (which carries the parent's seed coins) replaced by different seed words.
    {
        let (t, _s, _i) = mitm(&st, true, move |req| match req {
            Req::Round { stream, mut content, n } if stream == "blake3/rep0/f0" && content.len() > 64 => {
                let d = frame_domain(b"flock-par-assist-v1").len();
                content[d + 16] ^= 0x80;
                vec![Req::Round { stream, content, n }]
            }
            r => vec![r],
        });
        report("fork_child_seed_words_altered", "R3", "reject", &session(&st, t, &h()), json!({}));
    }

    // R2: one round split into two coin requests (before the fork, after it, and on a fork child).
    for (target, at_k) in [("blake3/rep0", 5usize), ("blake3/rep0", 80), ("blake3/rep1/f0", 10)] {
        let mut k = 0usize;
        let tgt = target.to_string();
        let (t, _s, _i) = mitm(&st, true, move |req| match req {
            Req::Round { stream, content, n } if stream == tgt => {
                k += 1;
                if k == at_k && content.len() >= 32 {
                    let (a, b) = content.split_at(16);
                    vec![Req::Round { stream: stream.clone(), content: a.to_vec(), n: 1 }, Req::Round { stream, content: b.to_vec(), n }]
                } else {
                    vec![Req::Round { stream, content, n }]
                }
            }
            r => vec![r],
        });
        report(&format!("round_split_in_two_{}_k{at_k}", target.replace('/', "_")), "R2", "reject", &session(&st, t, &h()), json!({}));
    }

    // R2: an extra coin round on rep 0 (and separately on a fork child) after the proofs are done.
    for extra_stream in ["blake3/rep0", "blake3/rep1/f0"] {
        let es = extra_stream.to_string();
        let (t, _s, _i) = mitm(&st, true, move |req| match req {
            Req::Finish => vec![Req::Round { stream: es.clone(), content: vec![0u8; 16], n: 1 }, Req::Finish],
            r => vec![r],
        });
        report(&format!("extra_round_after_proof_on_{}", extra_stream.replace('/', "_")), "R2", "reject",
               &session(&st, t, &h()), json!({}));
    }

    // R2: reps interleaved (rep 1 runs while rep 0 is still proving). Allowed by the server; recorded for the report.
    {
        let (t, s) = inproc(&st, true);
        call(&t, Req::Hello(SessionConfig::flock_128_r2(vec![st.spec()]).hello())).unwrap();
        call(&t, Req::Link(link_context(7))).unwrap();
        let st0 = st.clone();
        let t0 = t.clone();
        let h0 = std::thread::spawn(move || {
            let mut ch = LiveChallenger::new(t0, TABLE, 0, &domain(0)).unwrap();
            st0.prove(&blocks(0xA, st0.n), LigeritoProfile::Fast100, &mut ch)
        });
        loop {
            let rec = s.lock().unwrap().record_json();
            let committed = rec["streams"].as_array().unwrap().iter()
                .any(|x| x["stream"] == "blake3/rep0" && !x["root_sha256"].is_null());
            if committed { break; }
            std::thread::sleep(std::time::Duration::from_millis(1));
        }
        let mut ch1 = LiveChallenger::new(t.clone(), TABLE, 1, &domain(1)).unwrap();
        let p1 = st.prove(&blocks(0xA, st.n), LigeritoProfile::Fast100, &mut ch1);
        let p0_done_first = h0.is_finished();
        let p0 = h0.join().unwrap();
        call(&t, Req::Proof { table: TABLE.into(), rep: 0, bytes: p0 }).unwrap();
        call(&t, Req::Proof { table: TABLE.into(), rep: 1, bytes: p1 }).unwrap();
        let v: Value = match call(&t, Req::Finish) { Ok(Resp::Verdict(v)) => serde_json::from_str(&v).unwrap(), o => json!({"why": format!("{o:?}")}) };
        report("interleaved_reps", "R2 (informational)", "any", &v, json!({"rep0_finished_before_rep1": p0_done_first}));
    }

    // R7: hello variants and a third rep.
    let reordered = format!("{{\"reps\":2,\"profile\":\"fast100\",\"flavor\":\"rs\",\"tables\":[\"{TABLE}\"]}}");
    report("hello_keys_reordered", "R7", "reject", &session(&st, inproc(&st, true).0, &Plan { hello: Some(reordered), ..h() }), json!({}));
    report("hello_reps_3", "R7", "reject", &session(&st, inproc(&st, true).0,
        &Plan { hello: Some(json!({"profile":"fast100","reps":3,"flavor":"rs","tables":[TABLE]}).to_string()), reps: 3, witness: vec![0xA;3], profile: vec!["fast100";3], ..h() }), json!({}));
    {
        let (t, _s, _i) = mitm(&st, true, move |req| match req {
            Req::Finish => vec![Req::Open { stream: "blake3/rep2".into(), parent: String::new(), label: domain(2), at: 0 }, Req::Finish],
            r => vec![r],
        });
        report("third_rep_stream_opened", "R7", "reject", &session(&st, t, &h()), json!({}));
    }
    {
        let (t, _s, _i) = mitm(&st, true, move |req| match req {
            Req::Open { stream, parent, label: _, at } if stream == "blake3/rep1" =>
                vec![Req::Open { stream, parent, label: domain(0), at }],
            r => vec![r],
        });
        report("rep1_with_rep0_domain", "R7", "reject", &session(&st, t, &h()), json!({}));
    }
    // R7 with a Fast (not Fast100) proof whose params are relabelled Fast100: the transcript/schedule differ.
    {
        let (t, _s, _i) = mitm(&st, true, |r| vec![r]);
        let v = session(&st, t, &Plan { profile: vec!["fast", "fast"], ..h() });
        report("fast_proofs_in_r2_session", "R7", "reject", &v, json!({}));
    }

    // R5 / R8 as implemented: the link context is opaque, and a verifier started with --no-link accepts without it.
    report("arbitrary_link_bytes", "R5 (stub)", "any", &session(&st, inproc(&st, true).0, &h()), json!({"link": "flock-live/link-stub/v1||seed"}));
    {
        let (t, s) = inproc(&st, false);
        let v = session(&st, t, &Plan { send_link: false, ..h() });
        let rec = s.lock().unwrap().record_json();
        report("no_link_verifier_accepts_without_link", "R5/R8", "any", &v,
               json!({"record_require_link": rec["config"]["require_link"], "record_link_sha256": rec["link_sha256"]}));
    }
}

fn main() {
    let n: usize = arg("--n", "4096").parse().unwrap();
    attacks(Arc::new(Stmt::new(n)));
}
