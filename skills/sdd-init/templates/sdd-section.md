<!-- New instruction file only: offer this 2-line header above the section.
# {{PROJECT_NAME}}
{{STACK_LINE}}
-->
## SDD
- Specs dir: `{{SPECS_DIR}}` (feature folders `NNN-<slug>/` with spec.md, plan.md, tasks.md, progress.md)
- Verify (all): `{{VERIFY_CMD}}`
- Test: `{{TEST_CMD}}`
- Lint: `{{LINT_CMD}}`
- Typecheck: `{{TYPECHECK_CMD}}`
- Build: `{{BUILD_CMD}}`
- Test file patterns: `{{TEST_GLOBS}}`
- Commit convention: {{COMMIT_CONVENTION}} (`none established` if unknown)
- Documentation language: {{DOC_LANGUAGE}}
- Never:
  - Never weaken, skip, comment out or delete tests to make them pass.
  - Never edit spec.md or plan.md without explicit approval.
  - Never commit secrets or edit generated files.
