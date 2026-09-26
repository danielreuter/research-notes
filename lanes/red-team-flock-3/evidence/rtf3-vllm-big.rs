// red-team-flock-3 harness: does the vLLM block statement build from a netlist past 2^13 rows (PR #87 lifted UnitNet's cap)?
use flock_live::pure_block::UnitNet;
use flock_live::vllm_block::{Layout, VllmStmt};
fn main() {
    let a: Vec<String> = std::env::args().collect();
    let net = UnitNet::load(&a[1]);
    let useful = net.useful;
    let r = std::panic::catch_unwind(|| {
        let st = VllmStmt::new(net, 8, Layout::of(2048 * 2, 128));
        (st.digest.iter().map(|b| format!("{b:02x}")).collect::<String>(), st.m)
    });
    match r { Ok((d, m)) => println!("VLLM\tuseful={useful}\tBUILT m={m} digest={d}"), Err(_) => println!("VLLM\tuseful={useful}\tPANIC") }
}
