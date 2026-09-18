# Verified repair scope

The starting source was `f717379da9fd3e4e50b4d414a9f140519f034bcb`. The bundled example commands completed,
but there was no automated assertion suite. Bounded synthetic input probes
exposed the defect addressed here.

Reject whitespace/nontext evidence as missing, add opt-in strict gate, and printN/A for empty task mean.

New regression tests failed before the repair. After the change, `make verify`
passed 6 test methods, including independent result oracles and negative
command-line cases. Every original documented sample command was rerun. Test
counts are methods; parameterized inputs are not inflated into separate tests.

The tests use the standard library and synthetic fixtures. They do not claim
comprehensive schema validation, real model quality, external evidence quality,
or production readiness. CI repeats the discoverable verification command.
