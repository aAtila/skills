---
name: mac-disk-hygiene
description: >-
  Diagnose what's eating disk space on a Mac and reclaim it safely. Use this
  whenever the user is low on storage, can't install a macOS update for lack of
  space, asks "what's taking up all my space", wants to free up / clean up / clear
  out their disk, sees "Your disk is almost full", mentions purgeable space, or
  wants to clean caches, Docker, Xcode/simulator leftovers, node_modules, or
  package-manager junk. Trigger even when the user only describes the symptom
  ("my MacBook is full", "running out of space", "need 20GB free") without naming
  a tool. Measures first (read-only), ranks quick wins by space × safety, then
  cleans tier-by-tier with the user's confirmation — never deletes blindly.
---

# Mac Disk Hygiene

Help the user reclaim disk space on macOS without breaking anything. The guiding
principle is **measure, then cut** — most "clean my Mac" advice flips this and
deletes by reputation ("clear all caches!"). That's how people lose data or break
apps. Instead: get real numbers, rank what's worth removing against how safe it is
to remove, and let the user approve each tier.

This matters especially on small drives (256GB and under) where the user hits the
wall regularly and a 25GB Docker image or a forgotten simulator can be the
difference between updating macOS and not.

## Workflow

### 1. Scan (read-only, always safe)

Run the bundled scanner. It only measures — it never deletes:

```bash
bash <skill-dir>/scripts/scan.sh          # fast
bash <skill-dir>/scripts/scan.sh --deep   # also hunts node_modules in project roots
```

It prints four sections: **OVERVIEW** (free space + purgeable/snapshots),
**KNOWN RECLAIMABLE** (targets with a safe reclaim command, ranked by size),
**DISCOVERY** (big items hiding inside Containers / Application Support / Caches /
dotdirs that a naive scan misses — Docker and ML model caches love to hide here),
and **ACCOUNTING** (how much used space lives *outside* home + /Applications, i.e.
needs sudo).

Why a script and not ad-hoc `du`: the big wins are reliably the ones a one-liner
misses. Docker's VM image sits two levels deep inside `Containers/`; tool data
hides in dotdirs that `du ~/*` skips entirely. The script drills into those
parents every time so you don't rediscover them by hand.

### 2. Build the plan

Read the scan output and present a **ranked, tiered plan** — biggest, safest wins
first. Use the tier system below. For each item give: size, what it is, the tier,
and the exact reclaim command. Total up "easy reclaim" (the SAFE tier) separately
so the user sees the floor.

If the ACCOUNTING section shows a lot of space outside home+apps, say so plainly
and offer the `sudo` probes — don't pretend the home dir is the whole story.

### 3. Clean tier by tier, with confirmation

Deleting files is hard to undo, so confirm before each tier and **prefer the app's
own cleanup command over raw `rm`** (e.g. `brew cleanup`, `xcrun simctl delete
unavailable`, `docker system prune`). App-native commands know what's safe to drop
and keep the app's bookkeeping consistent; a blind `rm` can leave an app confused.

Start with the SAFE tier (regenerable caches — near-zero risk), confirm, execute,
then move to APP and CHECK tiers one at a time. Never batch-delete across tiers
without re-confirming.

### 4. Re-measure and report

After cleaning, re-run `df -h /` (or the scanner) and report actual space freed.
This closes the loop and catches the macOS gotcha where deleted space stays
"purgeable" until snapshots are thinned (see the catalog).

## The tier system

Everything you propose removing falls into one of these. Lead with the rationale,
not just the label — the user should understand *why* something is safe.

- 🟢 **SAFE — regenerable.** Caches and build artifacts the tool recreates on
  demand: `~/Library/Caches/*`, DerivedData, `~/.npm`, `~/.cache`, Homebrew cache,
  unavailable simulators. Worst case after deleting: the next build/launch is
  slightly slower while the cache rebuilds. Delete freely (with confirmation).

- 🟡 **APP-MANAGED — clean through the app.** Data an app owns where a raw `rm`
  could corrupt its state: Docker's disk image, browser profiles, Photos library.
  Use the app's prune/cleanup command or its UI, not `rm`.

- 🟠 **CHECK — inspect first.** Things that look like junk but might be wanted: Xcode
  Archives (needed to re-submit apps), old Node versions still referenced by a
  project, ML model caches that are expensive to re-download. Show the user what's
  there and let them decide.

- 🔴 **LEAVE ALONE.** `~/Library/Application Support/*` (app data, not cache),
  `Containers`/`Group Containers` (sandboxed app state), and anything under
  `/System`, `/Library`, `/private/var` unless you know exactly what owns it and
  why it's safe. SIP protects much of this anyway.

When unsure which tier something is, treat it as more dangerous, not less, and ask.

## Detailed reclaim commands and gotchas

For the per-target safe-removal commands, the macOS-specific traps (purgeable
space, APFS local snapshots, why `df` lies, Docker's hidden image, simulator
cleanup, node_modules hunting), and copy-pasteable cleanup recipes, read
`references/cleanup-catalog.md`. Pull it up when building the plan or before
executing a tier you're less sure about.
