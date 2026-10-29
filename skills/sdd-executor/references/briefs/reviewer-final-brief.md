Mode: final
Rigor: <standard | light>
Documents: <path>/spec.md, <path>/plan.md, <path>/tasks.md
Verify commands: test=<cmd>; lint=<cmd>; typecheck=<cmd>; build=<cmd or none>
Git base: <tree T0 or commit recorded at the start of the run>
Git head: <tree of the working tree now, or HEAD if everything is committed>
Paths of pre-existing changes to exclude: <paths or none>
User-ordered decisions on unpinned details: <none | ...>
Review the whole feature diff. Produce the AC coverage matrix: every AC# and E#
with status covered | partial | missing | manual | deferred, implementing file:line and proving
test file:line (manual: the plan's procedure; deferred: the task with Blocking: no).
