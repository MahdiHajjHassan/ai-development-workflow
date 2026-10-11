# AgentCrew | Planning, Implementation, and Review

> [!CAUTION]
> **Public workflow documentation.** This repository contains workflow documentation and example task templates; the application source is private. It does not publish a runnable agent orchestrator or executed test results. The storefront is an illustrative task, and diagrams explain the workflow.

AgentCrew connects a product request to an AI-assisted code change and a human approval decision. I designed the responsibilities and records so each stage has a clear input and output.

## Responsibilities

| Stage | Receives | Produces |
| --- | --- | --- |
| Product planning | User need and product context. | Requirements and acceptance criteria. |
| Delivery planning | Agreed scope. | Tasks, dependencies, and progress. |
| Technical review | Requirements and application constraints. | API contracts and implementation decisions. |
| Implementation | Task, decisions, and project conventions. | Code changes and a work record. |
| Quality review | Requirements and code changes. | Check results, findings, and requested corrections. |
| Human approval | Change and review record. | A decision to accept, revise, or defer. |

## Keep decisions available to the next stage

Project instructions describe conventions. Reusable skills guide recurring tasks. A task folder holds the request, design decisions, progress, and deliverables. Links between these records help the next person or agent understand why a change was made.

When a task resumes, recorded progress is checked against the current repository. This avoids continuing from an outdated assumption about the code.

## Example: an item-detail feature

The storefront uses an Express REST API and a JavaScript browser application. Its [task brief](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/examples/task-brief.md) defines the fields a shopper sees, missing-item behavior, identifier validation, and existing browsing behavior.

The [review checklist](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/examples/task-review.md) connects those requirements to the changed files and check results. A reviewer can request corrections, such as removing an internal cost field or fixing a not-found message, before the product owner approves the change.

[Project overview](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/README.md)
