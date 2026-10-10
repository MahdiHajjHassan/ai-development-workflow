# AgentCrew

> [!CAUTION]
> **Workflow showcase.**
> AgentCrew documents my AI engineering approach through a storefront example and task templates. The application source is private; this repository does not include a runnable orchestrator or executed check results. Diagrams are explanatory illustrations. This work is separate from my university final-year project and employer work.

## My AI engineering team: planning, implementation, and review

I designed an AI engineering workflow that carries a task's purpose all the way to review.
AgentCrew presents my approach to that work: give each responsibility a clear brief,
keep decisions with the task, and ask for evidence before accepting a change.

For a developer or product owner, the useful handoff is more than “the code is ready.”
It explains what changed, why it belongs in the product, and what still needs checking.
AgentCrew follows that handoff through a storefront task.

<picture>
  <source media="(max-width: 540px) and (prefers-color-scheme: dark)" srcset="assets/ai-story-v3-mobile-dark.svg">
  <source media="(max-width: 540px)" srcset="assets/ai-story-v3-mobile-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/ai-story-v3-dark.svg">
  <img src="assets/ai-story-v3-light.svg" width="680" alt="Planning, technical review, implementation, and quality review share a task brief and decisions. Review can request revision; the human owner accepts or defers the change.">
</picture>

### The context should travel with the task

A request can sound small and still contain several decisions.
Which behavior matters to the user? Which information can be shown?
What must keep working when the change is finished?

I defined the briefs, design decisions, and checkpoints.
I organized responsibilities around outputs another person can inspect.
The task record connects the request to the proposed change and the eventual review.

### One shopper, one bounded change

In the storefront, a shopper opens a catalog item to learn more before buying.
The requested change is an item-detail endpoint and a browser view.
Payment, authentication, inventory management, and checkout stay beyond this task.

The brief turns that simple interaction into specific expectations:

- A known item shows its public catalog fields.
- An unknown item gives a useful not-found message.
- Invalid identifiers receive consistent validation.
- Internal purchasing costs stay out of the response and the view.
- Existing catalog browsing continues to work.

The brief requires the public response contract and existing error convention to be settled before implementation.
Those choices tell the implementer where the task begins and ends.
They also give the reviewer something concrete to compare with the change.

### A handoff is an artifact

Planning produces the brief and acceptance criteria.
Delivery planning breaks the scope into tasks and dependencies; technical review resolves the boundaries.
Implementation should return a scoped diff and a work record.
Quality review should connect each requirement to the checks actually performed.

The review record connects each scenario to a command, observed behavior, and supporting evidence.
The owner can inspect the scope, requirement coverage, and remaining concerns before accepting a change.

I designed the acceptance boundary around the human responsible for the product:
accept the change, request a revision, or defer it with the remaining concerns recorded.

<details>
<summary><strong>Workflow mechanics, responsibilities, and review criteria</strong></summary>

### Responsibilities and outputs

| Responsibility | What the next stage receives |
| --- | --- |
| Product planning | Scope and acceptance criteria |
| Delivery planning | Tasks, dependencies, and progress |
| Technical review | Design choices and implementation boundaries |
| Implementation | Reviewable changes and a work record |
| Quality review | Observed checks, findings, and gaps |
| Human ownership | Decisions on tradeoffs, acceptance, and release |

### Recover the reasoning before continuing

Project instructions hold conventions and boundaries; reusable skills guide recurring work.
Task folders keep requests, decisions, progress, and deliverables together.
A linked knowledge base makes those records discoverable.
Continuation starts by checking the recorded state against the current repository.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/MahdiHajjHassan/ai-development-workflow/main/assets/review-workflow-dark.svg">
  <img src="https://raw.githubusercontent.com/MahdiHajjHassan/ai-development-workflow/main/assets/review-workflow-light.svg" width="680" alt="Existing reference diagram showing product and delivery planning, technical review, implementation, QA, revision paths, and a human release decision.">
</picture>

### What would send the task back for revision?

The review needs evidence for the actual diff, requirement coverage, and any extra scope.
An exposed purchasing-cost field, unclear invalid-ID behavior, or broken browsing would require correction.
Missing check evidence remains a gap; generated tests and assertions alone do not establish a pass.
The owner records the decision after reviewing the change and the evidence.

### Inspect the public artifacts

- [Workflow mechanics](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/docs/workflow.md): responsibilities, project context, and continuation.
- [Task brief](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/examples/task-brief.md): the item-detail scope, criteria, and open technical questions.
- [Review record](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/examples/task-review.md): scope review, check evidence, and the human decision.

The storefront context uses an Express REST API and a JavaScript browser application.

</details>

[Mahdi Hajj Hassan](https://github.com/MahdiHajjHassan)
