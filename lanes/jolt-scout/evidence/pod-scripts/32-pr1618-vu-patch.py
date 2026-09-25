"""jolt-scout: let PR #1618's `jolt-prover profile` prove an arbitrary guest. JOLT_PROFILE_GUEST names the guest crate
(memory config set to the vu-k1536 guest's #[jolt::provable] attributes) and JOLT_PROFILE_INPUT is a file of the
postcard input bytes; unset, the harness is unchanged."""
import pathlib
import sys

p = pathlib.Path(sys.argv[1])
s = p.read_text()
if "JOLT_PROFILE_GUEST" in s:
    sys.exit(0)
old_prog = '    let mut program = host::Program::new(&format!("{bench_name}-guest"));\n'
new_prog = '''    let guest_name = std::env::var("JOLT_PROFILE_GUEST").unwrap_or(format!("{bench_name}-guest"));
    let mut program = host::Program::new(&guest_name);
    if std::env::var("JOLT_PROFILE_GUEST").is_ok() {
        program.set_heap_size(33554432);
        program.set_stack_size(65536);
        program.set_max_input_size(8388608);
        program.set_max_output_size(65536);
    }
'''
old_in = "    let input = workload.input(bench_target);\n"
new_in = '''    let input = match std::env::var("JOLT_PROFILE_INPUT") {
        Ok(path) => fs::read(path).expect("read JOLT_PROFILE_INPUT"),
        Err(_) => workload.input(bench_target),
    };
'''
assert s.count(old_prog) == 1 and s.count(old_in) == 1
s = s.replace(old_prog, new_prog).replace(old_in, new_in)
s = s.replace(
    '    let trace_length = trace_output.trace.rows().len();\n',
    '    let trace_length = trace_output.trace.rows().len();\n    println!("MODULAR_TRACE_LEN {trace_length}");\n',
    1,
)
p.write_text(s)
print("patched", p)
