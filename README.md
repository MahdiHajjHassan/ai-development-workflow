# AI workflow reference

An independent reference demonstration of an AI workflow for a fictional storefront, with product planning, delivery planning, technical review, implementation, and QA. Human ownership covers system design, acceptance, and release decisions.

This repository contains documentation and illustrative task templates; the original application source remains private. It is separate from my final-year multi-agent orchestration project and contains no employer work.

## How the workflow is organized

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/review-workflow-dark.svg">
  <img alt="AI planning, implementation, and acceptance checks are guided by technical review, with revision paths and my final release decision." src="assets/review-workflow-light.svg" width="500">
</picture>

Each stage has a concrete output. A task carries requirements and constraints into implementation, QA checks the result, and feedback sends it back for revision. Passing an automated check does not replace the owner's decision about the design or release.

## Project context and review

- Versioned project instructions and reusable skills.
- Task folders that hold context, progress, and deliverables together.
- Staged changes that can be reviewed before acceptance.
- A linked knowledge base built from project documents.

The aim is to make decisions and changes easy to follow across tasks, instead of keeping the whole project in one long conversation.

## Technical detail and examples

- [Workflow mechanics](docs/workflow.md): responsibilities, artifacts, review, and continuation.
- [Example task brief](examples/task-brief.md): a fictional storefront change with bounded scope.
- [Example review record](examples/task-review.md): a blank evidence template, not a test-results claim.

[Mahdi Hajj Hassan](https://github.com/MahdiHajjHassan) · [Doctoleb](https://github.com/MahdiHajjHassan/doctoleb-showcase)
