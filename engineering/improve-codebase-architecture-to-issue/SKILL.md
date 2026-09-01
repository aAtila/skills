---
name: improve-codebase-architecture-to-issue
description: Run improve-codebase-architecture and land each deepening candidate as a tracker issue instead of an HTML report.
disable-model-invocation: true
---

# Improve codebase architecture → issue

Wraps `improve-codebase-architecture` with a tracker ledger: candidates land as open `architecture-review`-labeled issues instead of an HTML report, so findings persist as a backlog and re-runs skip what's already filed.

The base skill is user-invoked, so it cannot be reached through the Skill tool. Read `~/.claude/skills/improve-codebase-architecture/SKILL.md` directly and follow it, with these overrides:

- Run its **step 1 (Explore)** in full, exactly as written.
- Replace its **step 2 (HTML report)** with the ledger check and issue filing below. Skip `HTML-REPORT.md` entirely.
- Skip its **step 3 (grilling loop)**: the issues are the deliverable. When the user later picks an issue to act on, that's the moment to grill — note this in the final summary.

## Check the ledger

Before exploring, read the ledger so already-filed candidates are skipped.

Detect the host from `git remote get-url origin` (github.com → `gh`, gitlab domain → `glab`), then list open issues:

- GitHub: `gh issue list --label architecture-review --state open --json number,title,body`
- GitLab: `glab issue list --label architecture-review`

If an open issue already covers a candidate (same files, same deepening move), report the existing issue number instead of filing again. If the CLI is missing or unauthenticated, tell the user and stop — without a tracker this workflow has no output; point them at the base skill for the report-only run.

## File one issue per candidate

Each candidate card from the base skill's step 2 becomes one issue. Keep the card's content and vocabulary intact — files, problem, solution, benefits in terms of locality and leverage, recommendation strength, and any ADR-conflict callout.

1. Ensure the label exists (ignore "already exists"):
   - GitHub: `gh label create architecture-review --description "Deepening candidate from an architecture review" --color 1D76DB`
   - GitLab: `glab label create --name architecture-review --description "Deepening candidate from an architecture review" --color "#1D76DB"`
2. File it — title `arch: <one-line deepening description>`, body = the card in markdown. Render the before/after diagrams as ```mermaid fenced blocks (GitHub and GitLab both render them natively); drop any hand-crafted CSS/SVG visuals in favour of a mermaid or plain-text equivalent:
   - GitHub: `gh issue create --label architecture-review --title "..." --body "..."`
   - GitLab: `glab issue create --label architecture-review --title "..." --description "..."`
3. Mark the top recommendation: prefix its title with `arch(top):` and open its body with a line explaining why it goes first.
4. Report all issue URLs back to the user, top recommendation first.

Done when every candidate has an issue URL or a matched existing issue number.

## When this skill is the wrong fit

- Interactive session ending in a visual report and a grilling loop → `improve-codebase-architecture`
