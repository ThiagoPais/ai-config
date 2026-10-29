Mode: task
Rigor: <standard | light>
Task: <T#>
Documents: <path>/spec.md, <path>/plan.md, <path>/tasks.md
Verify commands: test=<cmd>; lint=<cmd>; typecheck=<cmd>; build=<cmd or none>
Test file conventions: <patterns>
Git base: tree <T>
Base kind: <post-test snapshot | pre-run>
Git head: tree <T2> (snapshot of the working tree now, untracked files included)
Test files written by the test-writer (post-test snapshot: unchanged since <T>; pre-run: hashes unchanged): <paths or none>
Test corrections: <none | tests corrected by test-writer after round N (reason)>
Paths of pre-existing changes to exclude: <paths or none>
User-ordered decisions on unpinned details: <none | ...>
Review the diff yourself (`git diff <T> <T2>`) against the documents and this
task's "Covers" and "Done when". Fail by default unless you can cite evidence.
