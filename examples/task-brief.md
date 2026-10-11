# AgentCrew | Item-Detail Task Brief

> [!CAUTION]
> **Public workflow documentation.** This repository contains workflow documentation and example task templates; the application source is private. It does not publish a runnable agent orchestrator or executed test results. The storefront is an illustrative task, and diagrams explain the workflow.

## User need

A shopper needs to inspect a catalog item's details before deciding whether to buy it.

## Requested change

An item-detail API endpoint and browser page in the existing storefront. The task covers catalog information and error handling. Checkout, payments, authentication, and inventory management are outside its scope.

## Acceptance criteria

| Situation | Required behavior |
| --- | --- |
| Known item | Return and display the public catalog fields. |
| Unknown item | Return not found and show a useful browser message. |
| Invalid identifier | Reject it using the application's validation convention. |
| Internal purchasing cost | Exclude it from both the API response and the page. |
| Existing browsing | Keep catalog browsing working. |

## Technical decisions to record

- The public response fields.
- The API's error format and identifier rules.
- The application routes and components affected.
- The checks covering the new page and existing browsing.

## Deliverables for review

Code changes limited to the agreed task, a record of the decisions, and check results linked to the acceptance criteria.

[Project overview](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/README.md) · [Review checklist](https://github.com/MahdiHajjHassan/ai-development-workflow/blob/main/examples/task-review.md)
