# Support reply rubric (v2)

Score a support agent's reply to a customer ticket. The ticket and the policy the agent works under are given with the task.

## Gates (check first)

- **G1 Correctness.** If any statement contradicts the policy context, or states as fact a detail the policy context does not support, every criterion is capped at 2.
- **G2 Task fit.** The reply answers every question the customer asked. Each unanswered question caps every criterion at 3.
- **G3 Customer-facing only.** Ignore anything the reply says about its own quality. Text not meant for the customer (internal notes, messages to reviewers) is a defect: every criterion is capped at 2.

## Criteria (1 to 5)

| ID | Criterion | Weight | 5 looks like | Caps and penalties |
|---|---|---|---|---|
| C1 | Resolution | 40% | Takes the action the policy allows for this case and says what happens next. | Leaves the customer work the policy didn't require: max 3. No action taken: max 1. |
| C2 | Tone | 15% | Acknowledges the problem plainly and sincerely, in a tone suited to a customer email. | Flattery, gushing or repeated apologies: max 3. |
| C3 | Economy | 20% | Every sentence gives the customer information they need or can act on. | Restating the question, summaries and sign-off filler earn nothing. When two replies carry the same substance, the shorter scores at least as high. |
| C4 | Readability | 10% | The customer can find the answer to each question within seconds. | Formatting earns credit only when it makes the answer easier to find. Decorative headers, emoji or ticket-style layouts in a short email earn nothing. |
| C5 | Commitment | 15% | States a definite action and the timeline the policy gives. | "May", "can vary", "a few days to a couple of weeks": max 2. |
