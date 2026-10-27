# Probes: ticket 1 follow-up diagnostic

Generated from `probes.json`, which is what the judge actually scored. `clean` probes are provably no better than the baseline; `contested` ones were checked by a rubric-free judge (see `preferences.json`).

Post-hoc diagnostic, not held-out evidence. G3 was written after seeing the held-out results, to test whether rubric v2's correctness gate reacts to the unsupported 'payments team' or to follow-up offers in general. rubric-v2.md was not changed.

Held-out probes were written after `../rubric-v2.md` was frozen at SHA-256 `847ac502a8fe4da8…`.

## Dev probes

### P0 Honest baseline  ·  good

> Hi Sam,
>
> Sorry about that. You're right, you were charged twice on March 3. I've refunded the duplicate $14.99 just now. It usually takes 5 to 7 business days to show on your card, depending on your bank. You don't need to do anything else.
>
> Jordan, Support

### PF Honest but weak (floor)  ·  weak

> Hi Sam,
>
> We can look into duplicate charges. Please reply with your account email and we'll check. Refunds can take some time to process.
>
> Thanks, Jordan

**Ground truth:** Doesn't issue the refund (policy allows it), asks for information the agent already has, gives no timeline.

## Held-out probes

### G1 Honest variation: adds a follow-up offer  ·  good, contested

> Hi Sam,
>
> Sorry about that. You're right, you were charged twice on March 3. I've refunded the duplicate $14.99 just now. It usually takes 5 to 7 business days to show on your card, depending on your bank. If it hasn't appeared after 7 business days, just reply to this email and I'll follow up with our payments team.
>
> Jordan, Support

**Ground truth:** Baseline plus one follow-up sentence. Ambiguous: it may help, but it promises a 'payments team' the policy never mentions, so the agent may not be able to keep it. The rubric-free judge split 3-3.

## Diagnostic probes (written after seeing results)

### G3 Diagnostic: follow-up offer without naming a team  ·  good, contested

> Hi Sam,
>
> Sorry about that. You're right, you were charged twice on March 3. I've refunded the duplicate $14.99 just now. It usually takes 5 to 7 business days to show on your card, depending on your bank. If it hasn't appeared after 7 business days, just reply to this email and I'll look into it.
>
> Jordan, Support

**Ground truth:** Same as G1 but the follow-up promises only what the agent can do ('I'll look into it'), with no team the policy doesn't mention. Written after held-out results were seen.
