# AgentCrew | Code Review Checklist

> [!CAUTION]
> **Public workflow documentation.** This repository contains workflow documentation and example task templates; the application source is private. It does not publish a runnable agent orchestrator or executed test results. The storefront is an illustrative task, and diagrams explain the workflow.

This checklist gives the reviewer a direct route from the item-detail requirements to the changed code and check results.

## Review the change

| Question | What to inspect |
| --- | --- |
| What changed? | The changed files and diff or commit. |
| Does it meet the task? | Each acceptance criterion and the code that addresses it. |
| Is the API contract clear? | Public fields, validation, and error responses. |
| Did the scope grow? | Additional changes and their reason. |

## Check the behavior

| Scenario | Record |
| --- | --- |
| Known item | Command, observed response, and page behavior. |
| Unknown item | Not-found response and browser message. |
| Invalid identifier | Validation response. |
| Internal fields | Response-field check and page inspection. |
| Existing catalog browsing | Regression-check output. |

## Approval decision

The product owner reviews the change and checklist, then records acceptance, requested corrections, or deferral. Remaining work has an owner and a clear next step.

[Task brief](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/examples/task-brief.md) · [Project overview](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/README.md)
