# Question bank (framework-neutral)

A menu for the interview, not a script. Pick the few questions whose answers would change the spec, skip what the repository or the user's input already answers, and turn the rest into `AskUserQuestion` options with a recommended default first. Questions about technology choices do not belong here; those are for the plan phase.

## Contents

1. Problem and users
2. Scope, non-goals and MVP
3. Behavior
4. Edge cases and errors
5. Constraints
6. Data and integration impact
7. Interface (only when relevant)
8. Physical / embedded / external-environment systems (only when relevant)
9. Closing checks

## 1. Problem and users

- Who is affected, and what are they unable to do or doing badly today?
- What triggers the need now? What happens if we do nothing?
- How will we know it worked (a measurable outcome, even a rough one)?
- Is there an existing workaround, and what makes it insufficient?

## 2. Scope, non-goals and MVP

- What is the smallest version that is still useful?
- What related things should explicitly NOT be part of this feature?
- Is anything a follow-up rather than part of this delivery?
- Does this replace or change an existing behavior that people rely on?

## 3. Behavior

- Describe the happy path step by step: who starts it, what they provide, what they get.
- Are there alternative paths (different entry points, optional steps, bulk vs single)?
- Which roles exist, and who may do what? What does an unauthorized actor see?
- What are the limits (counts, sizes, lengths, rate, retention)?
- What changes for the other parties involved (notifications, audit trail, side effects)?
- Is the action reversible? By whom, and until when?

## 4. Edge cases and errors

- Empty state: no data, first use, nothing selected.
- Duplicates and repeated actions (double submit, retry).
- Concurrency: two actors change the same thing at once.
- Deletion: what happens to dependent things when something is removed?
- Failure and offline: the dependency is down, the connection drops midway, the action partly completes.
- Validation: which inputs are invalid, and what message or outcome is expected?
- Boundaries: minimum, maximum, exactly-at-limit, just beyond.
- Permissions that change mid-flow (role revoked, session expired).

## 5. Constraints

- Performance: any latency, throughput or size target with a number?
- Privacy and compliance: personal data involved, retention, consent, regional rules?
- Security: authentication, authorization, data exposure, abuse cases?
- Platforms and compatibility: supported clients, versions, locales, accessibility level?
- Cost or operational limits: quotas, budget, support burden?
- Deadlines or sequencing dependencies on other teams or releases?

## 6. Data and integration impact

Flag, do not design. Record "needs update of <document>" in the spec's documentation-impact section.

- Does this introduce new kinds of information to store, or change the meaning of existing ones?
- Which external systems or other features does it read from or notify?
- Does it change a contract others depend on (API, events, file formats)?
- Does existing data need to be migrated, backfilled or cleaned?
- Which existing project documents describe the affected areas?

## 7. Interface (only when relevant)

- Which screens, commands or endpoints are involved, and where do users enter the flow?
- What states must be visible: loading, empty, error, success, disabled?
- What copy or message language is required, and who owns the wording?
- Any accessibility or localization requirement specific to this feature?

## 8. Physical / embedded / external-environment systems (only when relevant)

Skip entirely for purely software features. Answers here usually become assumptions (`[ENV]`).

- Units and measurement resolution: what unit, what smallest distinguishable change?
- Actuator and sensor limits: ranges, rates; what can be damaged if exceeded?
- Safe state on fault, reset or power loss: what must the system do, and what must it never do?
- Start trigger and unattended behaviour: who or what starts it; what happens with nobody watching?
- Duration: how long does one run last; what happens at the end?
- Sensor fault definition: what reading or absence counts as a fault, and the response?
- Environment assumptions: placement, ambient conditions, connection lifetime.
- If the process restarts at the worst moment, what is lost, and how do we know?
- Bring-up prerequisites (setup, credentials, power-on order). Flag as needs-plan-section: the spec records that they exist; the plan describes them.

## 9. Closing checks

- Is there anything you would be surprised NOT to see in the delivered feature?
- Is there anything that must NOT change?
- Who needs to approve this spec besides the requester?
- Which of today's answers are still guesses? (turn each into a `Q#`)
