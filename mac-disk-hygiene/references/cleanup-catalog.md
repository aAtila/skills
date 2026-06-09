# Cleanup Catalog — safe reclaim commands & macOS gotchas

Reference for building and executing the cleanup plan. Each entry: what it is, the
tier, and the safest way to reclaim. Prefer app-native commands over `rm`.

## Table of contents
- [macOS gotchas you must know](#macos-gotchas-you-must-know)
- [Developer / package-manager caches](#developer--package-manager-caches)
- [Xcode & iOS simulators](#xcode--ios-simulators)
- [Docker](#docker)
- [Browser & app caches](#browser--app-caches)
- [node_modules & project artifacts](#node_modules--project-artifacts)
- [System-level space (needs sudo)](#system-level-space-needs-sudo)
- [What NOT to touch](#what-not-to-touch)

---

## macOS gotchas you must know

**`df` lies on modern macOS.** On APFS the boot drive is split into a sealed,
read-only *System* volume and a *Data* volume that share one container. `df -h /`
often shows the tiny System volume. The number that matters is the **container
free space** from `diskutil info /` — that's what the scanner reports.

**Purgeable space.** macOS reports space as "used" that it can reclaim on demand
(old snapshots, cache files, redownloadable content). Finder's storage bar shows a
"Purgeable" slice. You can't always free it with `rm`; sometimes it clears only
under pressure or when snapshots are thinned.

**APFS local snapshots** (from Time Machine) can silently hold gigabytes. List and
thin them:
```bash
tmutil listlocalsnapshots /
# thin: free up to <bytes>, urgency 1 (low) .. 4 (high)
sudo tmutil thinlocalsnapshots / 21474836480 4   # try to free ~20GB
```
After deleting large files, freed space may stay purgeable until snapshots roll
off — re-check `diskutil info /` rather than trusting `df` immediately.

**SIP (System Integrity Protection)** blocks writes/deletes under `/System` and
parts of `/usr`, `/Library`. If a delete is "permission denied" there, that's SIP
doing its job — don't try to defeat it.

---

## Developer / package-manager caches

All 🟢 SAFE — these are pure caches; the tools refill them on next use.

| Target | Reclaim command |
|---|---|
| npm | `npm cache clean --force` |
| Yarn | `yarn cache clean` |
| pnpm | `pnpm store prune` |
| Bun | `bun pm cache rm` |
| Homebrew | `brew cleanup --prune=all` (and `brew autoremove`) |
| Gradle | `rm -rf ~/.gradle/caches` (rebuilds on next build) |
| CocoaPods | `pod cache clean --all` |
| Go build cache | `go clean -cache` |
| Rust/cargo | `cargo cache --autoclean` (needs `cargo-cache`) or trim `~/.cargo/registry/cache` |
| pip | `rm -rf ~/Library/Caches/pip` |
| Generic | inspect `~/.cache/*` and `~/Library/Caches/*` — most subdirs are app caches |

🟠 **CHECK:** `~/.nvm/versions` — old Node versions. `nvm ls` first; some may be
the default a project pins. `nvm uninstall <version>` to drop one.

---

## Xcode & iOS simulators

Big and easy on dev machines.

- 🟢 **DerivedData** — build intermediates, fully regenerable:
  `rm -rf ~/Library/Developer/Xcode/DerivedData/*`
- 🟢 **Unavailable simulators** — runtimes/devices for OS versions you no longer
  have: `xcrun simctl delete unavailable`
- 🟢 **Old iOS DeviceSupport** — symbol files per iOS version; Xcode re-downloads
  when you connect a device on that version. Delete old version folders in
  `~/Library/Developer/Xcode/iOS DeviceSupport/`.
- 🟠 **Archives** (`~/Library/Developer/Xcode/Archives`) — CHECK. These are your
  built `.xcarchive`s; you need them to re-submit/notarize a release. Keep recent
  ones, delete stale.
- 🟢 **Simulator devices data** (`CoreSimulator/Devices`) — `xcrun simctl delete
  unavailable` is the safe lever; to reset everything (loses sim app data):
  `xcrun simctl erase all`.

---

## Docker

Often the single biggest win on a dev Mac — the Linux VM disk image
(`~/Library/Containers/com.docker.docker/.../Docker.raw` or `docker.raw`) grows and
**does not shrink on its own**, even when the daemon is stopped.

🟡 **APP-MANAGED — never `rm` the .raw file.** Use Docker's own pruning:
```bash
docker system df                     # see what's using space
docker system prune -a --volumes     # remove unused images, containers, networks, volumes
docker builder prune -a              # build cache
```
If the image file is still huge after pruning, reclaim via **Docker Desktop →
Settings → Resources → Advanced** (lower disk image size) or **Troubleshoot →
Clean / Purge data**. If the user doesn't use Docker, uninstalling Docker Desktop
removes the whole image directory cleanly.

⚠️ `prune --volumes` deletes named volumes — that's real data (databases etc.).
Confirm the user doesn't need any volume data first.

---

## Browser & app caches

- 🟡 **Chrome/Brave/Edge cache** (`~/Library/Caches/Google`, etc.) — clearing via
  the browser (Settings → Privacy → Clear browsing data → Cached images/files) is
  cleaner than `rm`, though deleting the cache dir is generally safe too. Don't
  delete the *profile* (`~/Library/Application Support/Google/Chrome`) — that's
  bookmarks, history, logins.
- 🟠 **ML / model caches** (e.g. FluidAudio, HuggingFace `~/.cache/huggingface`,
  Ollama models `~/.ollama/models`) — CHECK. Large and re-downloadable, but the
  re-download can be gigabytes/slow. Confirm before removing.
- 🟢 **App caches generally** — `~/Library/Caches/<app>` is regenerable. The app's
  *Application Support* and *Containers* dirs are NOT cache — leave those.

---

## node_modules & project artifacts

🟠 **CHECK (per project).** `node_modules` in dormant projects is dead weight —
reinstall with `npm/yarn/pnpm install` when you return to the project. Run the
scanner with `--deep` to list the biggest ones, then:
```bash
# safe: only removes node_modules, never source
find ~/CODE -maxdepth 4 -type d -name node_modules -prune -exec du -sh {} \;
# delete a specific one:
rm -rf /path/to/project/node_modules
```
Tools like `npkill` (`npx npkill`) give an interactive picker. Only remove from
projects the user isn't actively building. Other reclaimable build artifacts:
`.next`, `dist`, `build`, `target` (Rust), `.gradle` project caches, Pods/.

---

## System-level space (needs sudo)

If ACCOUNTING shows lots of space outside home+apps, investigate with the user
running these (they prompt for a password — suggest the user run them via `!` in
the session so output lands here):
```bash
sudo du -xhd 1 /System/Volumes/Data 2>/dev/null | sort -h | tail -15
sudo du -xhd 1 /private/var 2>/dev/null | sort -h | tail -10
sudo du -xhd 1 /Library 2>/dev/null | sort -h | tail -10
```
Common system-level consumers: `/private/var/vm` (sleepimage/swap — managed by
macOS, leave it), `/Library/Developer/CoreSimulator` (shared sim runtimes —
`xcrun simctl delete unavailable` covers these), other user accounts, and large
files in `/private/var/folders` caches.

---

## What NOT to touch

🔴 Leave these alone unless you know exactly what a specific subitem is:
- `~/Library/Application Support/*` — app *data* (settings, projects, databases),
  not cache. Deleting loses real work.
- `~/Library/Containers/*` and `~/Library/Group Containers/*` — sandboxed app
  state. (Exception: an app's own *cache* subfolder inside, but be precise.)
- Anything under `/System`, much of `/Library`, `/usr` — SIP-protected and/or
  OS-critical.
- `/private/var/vm` — swap/sleepimage, managed by macOS.
- Mail, Messages, Photos libraries via `rm` — clean through the app instead, or
  you'll corrupt the library.

Golden rule: **cache = safe, data = dangerous.** When a path's name doesn't make
the distinction obvious, treat it as data and ask.
