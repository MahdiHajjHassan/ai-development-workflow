# AgentCrew | AI Software Delivery Workflow

> [!CAUTION]
> **Public workflow documentation.** This repository contains workflow documentation and example task templates; the application source is private. It does not publish a runnable agent orchestrator or executed test results. The storefront is an illustrative task, and diagrams explain the workflow.

## Turn a feature request into a reviewable software change

AgentCrew is an AI-assisted delivery workflow for developers and product owners. It connects requirements, technical planning, implementation and quality review, with a person deciding whether the resulting change is ready or needs revision.

**My contribution:** I designed the stages, agent responsibilities and task records, defined the information passed between stages, and placed human approval at the design and change-review points.

<picture>
  <source media="(max-width: 540px) and (prefers-color-scheme: dark)" srcset="assets/ai-story-v5-mobile-dark.svg">
  <source media="(max-width: 540px)" srcset="assets/ai-story-v5-mobile-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/ai-story-v5-dark.svg">
  <img src="assets/ai-story-v5-light.svg" width="680" alt="A feature request becomes a shared plan and task brief. Implementation produces code changes, quality review returns findings, and a product owner approves the change or requests a revision that returns to implementation.">
</picture>

### What I designed

- **A shared task brief:** the user need, expected behavior and scope travel with the task.
- **Specialist responsibilities:** planning, technical review, implementation and quality review each produce an output for the next stage.
- **Traceable decisions:** requirements, design choices, progress and deliverables stay connected in the task record.
- **A revision path:** review findings return to implementation, and the product owner can accept, revise or defer the change.

### Follow one feature through the workflow

The storefront task is an item-detail API endpoint and browser page. A shopper needs public item information; the response must handle invalid or missing identifiers and exclude internal purchasing costs.

| Stage | Work for this task | Handoff |
| --- | --- | --- |
| Product planning | Define what the shopper needs and the expected behavior. | Requirements and acceptance criteria. |
| Technical review | Agree on response fields, error handling and affected application areas. | API contract and implementation scope. |
| Implementation | Prepare the endpoint and page changes. | Code changes and a record of the work. |
| Quality review | Compare the change with the agreed behavior. | Findings and requested corrections. |
| Human approval | Inspect the result and decide whether it is ready. | Acceptance or a return to revision. |

A reviewer can follow a requirement from the brief to the implementation and its review record. The product owner retains the final decision about the change.

<details>
<summary><strong>Engineering details: agent responsibilities, task records, and review</strong></summary>

### Coordination and continuity

Product planning establishes acceptance criteria. Delivery planning organizes tasks, dependencies and progress. Technical review defines contracts and scope before implementation; quality review records findings afterward.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/MahdiHajjHassan/ai-development-workflow/main/assets/review-workflow-dark.svg">
  <img src="https://raw.githubusercontent.com/MahdiHajjHassan/ai-development-workflow/main/assets/review-workflow-light.svg" width="680" alt="Engineering workflow: product and delivery planning, technical review, implementation, QA, revision paths, and a human release decision.">
</picture>

### Task records

I organized requests, decisions, progress and deliverables together. Project instructions hold coding conventions, reusable skills describe recurring work, and a linked knowledge base makes decisions available to the next stage. Before resuming, the workflow compares recorded progress with the current repository.

### Review criteria

The item-detail review covers public response fields, invalid and missing identifiers, internal-field exclusion and existing catalog browsing. The task record connects these criteria to the changed code and reported checks.

The example application uses an Express REST API and a JavaScript browser application.

- [Workflow responsibilities and handoffs](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/docs/workflow.md)
- [Item-detail task brief](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/examples/task-brief.md)
- [Code review checklist](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/examples/task-review.md)

</details>

[Back to my portfolio](https://github.com/MahdiHajjHassan)
