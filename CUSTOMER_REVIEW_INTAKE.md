# Authorized upgrade-review evaluation

Status: blank research instrument. No answers or customer validation exist yet.

## Who and what

- Reviewer role and team; who approves tooling expenditure?
- Last difficult upgrade date; exact chart, source/target versions and application images.
- Why was the upgrade required? What happened, or what is blocking approval now?
- Number of comparable reviews in the last 90 days, backed by an internal count if available. Separate observation from estimate.

## Existing process

- Which update, diff, validation, policy and coding-assistant tools were used?
- What did they find? Which step required manual investigation?
- What sources did the reviewer consult? Was the issue already documented?
- Record time spent gathering inputs, reviewing sources, correcting output and resolving unknowns. A retrospective estimate must be labeled as one.

## Evaluation scope and permission

- Is this historical, staging or a pending production change? Start with a non-production review.
- Is the team authorized to share the chosen artifacts? Which fields must remain local?
- Supply sanitized values/rendered manifests and public migration links. No kubeconfig, cloud keys, secrets or unredacted application data.
- Identify facts only the team can verify: external controller version, actual CRD state, completed prerequisite, ownership or runtime result.
- Agree on one independent reviewer and expected findings before inspecting our output. If unavailable, label the evaluation author-only.

## Compare outcomes

- Did our report change any actual review decision? What exact evidence supported it?
- Which requirement did it miss or falsely flag?
- Did preparation plus review take less total effort than the team's normal process?
- Would the team use it on the next comparable upgrade? Who would authorize a bounded paid pilot, and what result would justify payment?
- What would make the team reject it even if the checker is technically correct?

Evidence ranking: an authorized real case and repeated usage are stronger than hypothetical interest; a paid pilot is stronger than compliments. No adoption, sale or saving should be recorded before it happens.
