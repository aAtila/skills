# Developer storage

Read when developer tools, agent directories, or a large application-data folder
appear in the scan. These are discovery patterns; remeasure and verify ownership
on each machine. Paths below are examples under the current user's home.

- [Swift build outputs and external copies](#swift-build-outputs-and-external-copies)
- [RepoPrompt CE Conductor cache](#repoprompt-ce-conductor-cache)
- [Agent caches and failed telemetry](#agent-caches-and-failed-telemetry)
- [Android SDK components](#android-sdk-components)
- [Project dependencies](#project-dependencies)

## Swift build outputs and external copies

**Discover:** Measure the project's `.build`, including debug/release products,
package checkouts, binary artifacts, and embedded runtime downloads. Check for
external build caches too: deleting one clone may leave shared blocks referenced
by another copy.

**Verify:** Read the repository's cleanup target and local instructions. Check
whether `.build` contains local reports or manually modified dependencies worth
preserving. Confirm that no build is writing there and that a running app/CLI is
not executing from the directory. A separately installed app may be independent;
verify its executable location rather than assuming it.

**Clean:** Use the repository's cleanup command after approval. For example, the
observed RepoPrompt CE `make clean` removes `.build`; check the current Makefile
before running it. The next build may download dependencies and compile from
scratch. Auxiliary format tools or generated IDE workspaces may need their own
setup commands rather than appearing on every build.

**Verify:** Confirm the target disappeared and remeasure free space. Use the
[accounting guidance](cleanup-catalog.md#storage-accounting-and-access) when the
measured size and recovery differ.

## RepoPrompt CE Conductor cache

**Discover:** Inspect this specific subdirectory when RepoPrompt CE application
storage is large:

```text
~/Library/Application Support/RepoPrompt CE/Conductor/BuildCache
```

The observed implementation stores reusable SwiftPM build seeds here, separately
from the checkout's `.build`. Sibling Codex session databases, workspaces, and
conversation history are application data, not part of this cache.

**Verify:** Find the relevant checkout from local project context. Inspect its
current `conductor cache` help/source, then run from that checkout:

```bash
./conductor cache status --json
```

Check the returned store path, entries, and cache keys; an environment override
may redirect the store. Treat the metadata size as an estimate and compare it
with disk usage. The observed implementation creates APFS clones, so separate
path sizes can refer to shared storage.

**Clean:** For each approved entry:

```bash
./conductor cache drop <key-from-current-status> --json
```

The native command coordinates deletion with per-key locks. Use it instead of
removing the whole Conductor parent. If a command waits on an active user of the
cache, inspect the job before proceeding; don't bypass its lock.

**Verify:** The approved key should be absent from `cache status`, and its cache
directory should be gone. Remeasure host free space. Future builds can repopulate
this cache; inspect the current tool's retention configuration if recurring growth
becomes a separate concern.

## Agent caches and failed telemetry

**Discover:** Inspect these narrow candidates when present:

| Candidate | Ownership check |
|---|---|
| `~/.npm/_npx` | Temporary downloaded npx packages; check for active commands using them. |
| `~/.cache/codex-runtimes` | Downloaded runtime dependencies; verify current ownership and whether tasks are executing from them. |
| `~/Library/Caches/org.swift.swiftpm` | Shared Swift package cache; check active builds. |
| `~/.claude/telemetry/1p_failed_events.*.json` | Failed telemetry queue files; inspect the exact set and file structure. |

Cache paths are candidates, not permanent API contracts. Confirm their contents
before using scoped removal. Do not extend approval to an entire agent home.

For Claude telemetry, observed `.json` files contained **JSON Lines** records with
`event_type` and `event_data` keys. Parse a line rather than assuming one JSON
object per file. Inspect only structure needed for classification; avoid printing
payloads that may contain sensitive data. Count regular matching files and report
unmatched entries separately. Reject symlinks and preserve unexpected files.

After approval, remove only the verified regular files matching
`1p_failed_events.*.json` directly inside the telemetry directory. Preserve
`~/.claude/projects`, settings, credentials, and other state. Check the remaining
file count and allocated size; a running application may enqueue new events.

Do not classify `.codex/sessions`, `.codex/sqlite`, or RepoPrompt CE's Codex session
store as disposable just because they are large. They hold task history/state.

## Android SDK components

**Discover:** Resolve the actual SDK and AVD locations from environment variables,
project `local.properties`, or Android Studio settings. Common defaults are:

```text
~/Library/Android/sdk
~/.android/avd
```

Respect `ANDROID_HOME`, `ANDROID_USER_HOME`, and `ANDROID_AVD_HOME` overrides.
`ANDROID_SDK_ROOT` may occur in older configurations; verify which path the active
toolchain uses. Inventory the selected SDK with its installed package manager or
Android Studio's SDK Manager. `<sdk>/emulator/emulator -list-avds` lists devices
without booting them when that executable is available.

Measure these independently:

| Directory/component | Consequence of removal |
|---|---|
| AVD directories | Erases virtual-device apps, snapshots, and saved data. |
| `system-images` | Requires downloading Android OS images before using matching AVDs. |
| `emulator` | Removes the emulator program; it can occupy space even with no AVDs/images. |
| `platform-tools`, including `adb` | Needed for device communication, installing APKs, logs, and shell access. |
| `platforms`, `build-tools`, NDK/CMake | Local build dependencies; required versions depend on the project. |
| Command-line SDK management | Useful for installing/removing SDK packages; separate from both `adb` and the emulator. |

**Clean:** For a user who uses only physical devices, emulator software and OS
images can be selected without removing the build SDK or `adb`. Use the installed
SDK manager's supported removal command, or Android Studio > SDK Manager > SDK
Tools > Android Emulator. If `sdkmanager` is available, its package removal form
is `sdkmanager --sdk_root=<verified-sdk> --uninstall emulator`; consult local help
for other/newer SDK CLIs. Delete selected AVDs through Device Manager or
`avdmanager delete avd -n <approved-name>` when available.

If package-management tooling is absent or unusable, a fallback can remove only
the verified self-contained `<sdk>/emulator` package directory after approval and
an active-process check. Do not install a new SDK, accept a setup wizard's default
downloads, or remove the whole SDK just to perform this cleanup. Report that the
fallback was used.

**Verify:** Confirm the selected device/package is absent and its files removed;
confirm retained `platform-tools/adb`, platforms, and build tools still exist.
Then measure host free space. A stale UI inventory is not proof of a failed or
successful filesystem deletion; refresh it when practical.

## Project dependencies

The deep scan looks for `node_modules` and `.build` in common project roots.
Custom worktrees or deeply nested packages can fall outside its bounded search.
Inspect only relevant additional roots when the scan suggests missing storage.

`node_modules`, Pods, `.next`, Rust `target`, and other generated outputs can be
large. Verify the project is inactive, dependency locks/install steps exist, and
no wanted local modifications are stored there. Select paths individually. Their
presence in a deep-scan result is not approval to remove them.
