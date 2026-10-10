# Example task brief

> [!CAUTION]
> **Workflow showcase.**
> AgentCrew documents my AI engineering approach through a storefront example and task templates. The application source is private; this repository does not include a runnable orchestrator or executed check results. Diagrams are explanatory illustrations. This work is separate from my university final-year project and employer work.

The task contract connects a shopper's need to an endpoint, browser view, and review criteria.

## Product need

A shopper needs to inspect a catalog item's details before deciding whether to buy it.

## Scope

Add an item-detail endpoint and browser view within the existing storefront. Payment, authentication, inventory management, and checkout are outside this task.

## Acceptance criteria

- A known identifier returns the item's public catalog fields.
- An unknown identifier produces a not-found response and a useful browser message.
- Invalid identifiers are rejected consistently.
- Internal purchasing-cost fields are absent from API responses and the view.
- Existing catalog browsing continues to work.

## Technical-review questions

- What is the existing API error convention?
- Which fields belong in the public response contract?
- Which existing browsing tests should run again?

## Implementation boundary

Resolve those questions against the application before writing changes. Use fixtures that match the public catalog contract. Prepare a scoped diff and record executed checks in the companion review record.

[Project overview](../README.md) · [Review record](task-review.md)
