---
id: 62F41A70-4741-4E3B-A785-5AF82BD82138
name: "PR Review Panel"
icon: "eye.fill"
tooltip: "Review a PR with independent Oracles and consolidate the findings."
description: "Run parallel Oracle reviews, verify findings against source, and deliver one consolidated verdict."
---

# PR Review Panel

PR: $ARGUMENTS

1. Resolve the PR’s base and head to commit SHAs and determine their merge base. Pin the review to the merge-base-to-head diff and source at that head.
2. Call `context_builder` with `response_type: "review"`, `oracle_preset: "PR-Review-Panel"`, and `export_response: true`. Provide the pinned comparison, PR intent, and any relevant spec; require review context from that same snapshot.
3. Once every reviewer has completed or failed, read every available result, deduplicate findings, and verify every finding you retain against the pinned source. Resolve disagreements using evidence, not majority voting.
4. Return one consolidated review containing the reviewed commit range, findings with severity, file/line location, and supporting evidence, a verdict, and any coverage gaps or failed reviewers.

Do not modify the code.
