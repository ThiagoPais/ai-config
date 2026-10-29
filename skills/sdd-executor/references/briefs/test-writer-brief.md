Task: <T#> - <title>
Criteria to cover: <AC#, E# list>
Done when: <the task's Done when text>
Documents: <path>/spec.md, <path>/plan.md, <path>/tasks.md
Test conventions: framework <name>; test files go in <location/pattern>;
  narrow command to run only the new tests: <command>
Correction diagnosis: <none | test, what it asserts, why it contradicts criterion/plan>
Existing modules this task changes: <module path + public signature as plan.md states it, or none>
Write failing tests for the criteria above. Do not read or modify implementation
code; import symbols from the paths plan.md names. Run the narrow command and report
each test's failure reason. Flag any criterion that is not testable as written, and
list every assumption you made. Check that each literal you assert (strings, ids,
formats) comes from the brief, spec or plan, not from your own invention.
