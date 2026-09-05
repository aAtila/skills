---
name: mac-disk-hygiene
description: >-
  Diagnose disk usage on a Mac and reclaim space safely. Use when storage is low,
  a macOS update needs more room, or the user wants to inspect or clean caches,
  Docker storage, simulators, build outputs, or package-manager downloads.
  Measures first, identifies ownership and cleanup methods, and removes only
  authorized targets before verifying actual space recovery.
---

# Mac disk hygiene

Measure before deleting. Identify what owns each large item, whether it can be
recreated, and what the user would lose by removing it.

## 1. Scan

Run the read-only scanner:

```bash
bash <skill-dir>/scripts/scan.sh
bash <skill-dir>/scripts/scan.sh --deep  # also find project dependencies/build outputs
```

It reports free space, candidate directories, large storage parents, and a rough
accounting check. A candidate's measured size is not its reclaimable size. Missing
permissions or unavailable services mean unknown, not empty or corrupt.

Follow the largest findings. Inspect large Application Support, Containers, and
dot-directories one level deeper to distinguish caches, runtime downloads, build
copies, databases, and user content. A parent directory is an investigation lead,
not a deletion target. Verify unfamiliar paths against the owning app's commands,
configuration, or source before classifying them.

Read [cleanup-catalog.md](references/cleanup-catalog.md) for APFS accounting,
Docker engines, iOS simulator storage, and standard cleanup commands. When the
scan finds developer or agent-tool storage, read
[developer-storage.md](references/developer-storage.md) for Swift build copies,
Conductor, failed telemetry, and Android SDK components.

Finish discovery with measured, non-overlapping targets and explicit unknowns.
Use scoped follow-up measurements instead of repeatedly scanning the whole home.

## 2. Classify and propose

For each candidate give its size, owner/purpose, consequence of removal, tier, and
exact cleanup command or app action. Keep these distinctions:

| Tier | Meaning |
|---|---|
| SAFE | Verified regenerable caches/build outputs. Check for active users of the files before cleaning. |
| APP-MANAGED | Use the owning app's cleanup mechanism to preserve its bookkeeping. This describes the method, not permission to delete its data. |
| CHECK | Inspect and select first: device data, archives, downloads, Trash, project dependencies, installed tool versions, models, or unfamiliar files. |
| LEAVE ALONE | Unclassified application/user data and protected system state. Investigate ownership rather than deleting the parent. |

A verified cache inside Application Support can be a cleanup candidate. Conversely,
a file inside a cache directory can hold costly model weights or a runtime in use.

Sum only non-overlapping, approved candidate estimates. Label the sum as an
estimate, never a guaranteed minimum: APFS clones, shared image layers, snapshots,
and concurrent disk activity can change recovery. Ask for missing usage context
when it changes the decision; an unreferenced image may still be wanted later.

## 3. Clean the authorized scope

Obtain approval for concrete targets and consequences. Existing approval for
those targets remains valid; continue without asking again for the same action.
A broader target, another tier, or data loss outside the approved scope needs new
approval. Explicit approval can cover a named batch across tiers.

Prefer app-native cleanup commands. Recheck target identity and relevant active
builds/devices before removal. For Docker, bind every command to the verified
engine/context. Remove selected items, preserving other versions and data volumes.

If a preferred tool is unavailable, identify why. A narrowly scoped fallback is
reasonable for a verified self-contained disposable package or cache. Avoid
turning a cleanup into an extended app-setup or repair task. Do not bypass system
protections or reset a broken VM to reclaim space.

## 4. Verify

Measure free space immediately before and after each approved batch using the same
filesystem, normally `df -k /System/Volumes/Data`, with `diskutil info /` for APFS
container information when available. Confirm the owning tool no longer lists the
target and check whether its backing files remain.

Report separately:

- What was removed, and any incomplete removal or retained download.
- Observed net free-space change and current free space.
- Any relevant re-download/rebuild cost.

An unregistered runtime with a retained system asset is not full disk recovery.
A mismatched size is not proof of snapshots or corruption; report the observation
and verify the cause before prescribing additional cleanup.
