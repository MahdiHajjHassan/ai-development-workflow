# Workflow mechanics

> [!CAUTION]
> **Workflow showcase.**
> AgentCrew documents my AI engineering approach through a storefront example and task templates. The application source is private; this repository does not include a runnable orchestrator or executed check results. Diagrams are explanatory illustrations. This work is separate from my university final-year project and employer work.

I designed AgentCrew around a storefront with an Express REST API and a JavaScript browser application. The workflow connects product intent, bounded implementation, quality review, and human acceptance.

## Responsibilities and artifacts

| Responsibility | Input | Output |
| --- | --- | --- |
| Product planning | Problem and intended users | Scope and acceptance criteria |
| Delivery planning | Approved scope | Tasks, dependencies, and progress |
| Technical review | Requirements and system constraints | Design choices and implementation boundaries |
| Implementation | Bounded task and project rules | Reviewable changes and a work record |
| Quality review | Acceptance criteria and changes | Check results, findings, and remaining gaps |
| Human ownership | Design choices and review evidence | Tradeoffs, acceptance, and release decisions |

Agents can carry out responsibilities without taking ownership of the product. Human ownership remains with the person responsible for the system and the final decision.

## Keep context in the project

Project instructions describe conventions and boundaries. Skills guide recurring work. A task folder keeps the request, decisions, progress, and deliverables together. The knowledge base links those documents so future work can recover the reasoning behind a change.

A continuation starts from the recorded state and current repository, rather than assuming remembered conversation text is authoritative.

## Review changes and evidence separately

Staging makes a proposed change inspectable before acceptance. QA compares it with the acceptance criteria and records the exact checks performed. An unexecuted check stays unexecuted; a generated test or an agent's assertion is not a passed result.

The [review record](../examples/task-review.md) illustrates how to collect this evidence. It links each criterion to the evidence required for acceptance.

[Project overview](../README.md)
