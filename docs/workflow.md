# Workflow mechanics

This documents my independent personal approach. The storefront demonstration uses an Express REST API and a JavaScript browser application; this repository provides documentation and illustrative templates, not that application's private source.

## Responsibilities and artifacts

| Responsibility | Input | Output |
| --- | --- | --- |
| Product planning | Problem and intended users | Scope and acceptance criteria |
| Delivery planning | Approved scope | Tasks, dependencies, and progress |
| Technical review | Requirements and system constraints | Design choices and implementation boundaries |
| Implementation | Bounded task and project rules | Reviewable changes and a work record |
| Quality review | Acceptance criteria and changes | Check results, findings, and remaining gaps |
| Human ownership | Design choices and review evidence | Tradeoffs, acceptance, and release decisions |

Agents can carry out responsibilities without taking ownership of the product. I remain responsible for the system and the final decision.

## Keep context in the project

Project instructions describe conventions and boundaries. Skills guide recurring work. A task folder keeps the request, decisions, progress, and deliverables together. The knowledge base links those documents so future work can recover the reasoning behind a change.

A continuation starts from the recorded state and current repository, rather than assuming remembered conversation text is authoritative.

## Review changes and evidence separately

Staging makes a proposed change inspectable before acceptance. QA compares it with the acceptance criteria and records the exact checks performed. An unexecuted check stays unexecuted; a generated test or an agent's assertion is not a passed result.

The [review record](../examples/task-review.md) illustrates how to collect this evidence. It contains no fabricated pass results.

## Demonstration boundary

The original demonstration stages a small API change within a fictional storefront. This showcase explains the process. It does not provide a runnable agent orchestrator, publish employer work, or establish production deployment or measured productivity gains.

[Project overview](../README.md)
