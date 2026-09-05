# Developer storage

Use the relevant section for the current target. Paths and commands below are
observed examples; check current ownership and tool behavior before removal.

- [Swift build outputs and external copies](#swift-build-outputs-and-external-copies)
- [RepoPrompt CE Conductor cache](#repoprompt-ce-conductor-cache)
- [Agent caches and failed telemetry](#agent-caches-and-failed-telemetry)
- [Android SDK components](#android-sdk-components)
- [Project dependencies](#project-dependencies)

## Swift build outputs and external copies

`.build` can contain debug/release products, package checkouts, binary artifacts,
and runtime downloads. External build caches may share its APFS blocks; see
[storage accounting](cleanup-catalog.md#storage-accounting-and-access).

Check for locally modified dependencies or reports worth preserving, and for
builds or executables using the directory. A separately installed app may be
independent; its executable path settles that question.

Use the repository's cleanup target. RepoPrompt CE's observed `make clean` removes
`.build`; confirm the current Makefile. Rebuilding may download and compile
dependencies. Auxiliary format tools or generated IDE workspaces may need separate
setup commands.

## RepoPrompt CE Conductor cache

```text
~/Library/Application Support/RepoPrompt CE/Conductor/BuildCache
```

This stores reusable SwiftPM build seeds separately from the checkout's `.build`.
Sibling Codex databases, workspaces, and conversation history remain application
data. The observed cache uses APFS clones.

From the relevant checkout, check current `conductor cache` help/source and inventory:

```bash
./conductor cache status --json
```

Use the returned store path and keys; environment overrides can redirect the store.
Compare metadata sizes with disk usage. For an approved entry:

```bash
./conductor cache drop <key-from-current-status> --json
```

The native command coordinates deletion with per-key locks. If it waits, inspect
the active job rather than bypassing the lock. Completion means the key is absent
from status and its directory is gone. Future builds can repopulate the cache.

## Agent caches and failed telemetry

| Candidate | Ownership check |
|---|---|
| `~/.npm/_npx` | Temporary downloaded npx packages; check active commands. |
| `~/.cache/codex-runtimes` | Downloaded runtime dependencies; check ownership and executing tasks. |
| `~/Library/Caches/org.swift.swiftpm` | Shared Swift package cache; check active builds. |
| `~/.claude/telemetry/1p_failed_events.*.json` | Failed telemetry queue; verify file structure and the selected set. |

Observed Claude `.json` files contain JSON Lines records with `event_type` and
`event_data` keys. Inspect structure without printing event payloads. Remove only
verified regular matching files directly inside the telemetry directory; preserve
symlinks and unexpected entries. A running app may enqueue new events during cleanup.

Agent homes also hold user data. Preserve Claude projects/settings/credentials,
`.codex/sessions`, `.codex/sqlite`, and RepoPrompt CE's Codex session store.

## Android SDK components

Common defaults are `~/Library/Android/sdk` and `~/.android/avd`. Resolve actual
locations from environment, project `local.properties`, or Android Studio settings.
Relevant overrides include `ANDROID_HOME`, `ANDROID_USER_HOME`, `ANDROID_AVD_HOME`,
and the older `ANDROID_SDK_ROOT`.

Inventory packages through the installed SDK manager. When available,
`<sdk>/emulator/emulator -list-avds` lists devices without booting them.

| Component | Consequence of removal |
|---|---|
| AVD directories | Loses virtual-device apps, snapshots, and saved data. |
| `system-images` | Matching AVDs need OS images downloaded again. |
| `emulator` | Removes the emulator program, which can occupy space even with no AVDs/images. |
| `platform-tools`, including `adb` | Removes device communication, APK installation, logs, and shell tools. |
| `platforms`, `build-tools`, NDK/CMake | Removes local build dependencies; required versions depend on the project. |
| Command-line SDK management | Removes package-management tools, separate from both `adb` and the emulator. |

Physical-device users can remove emulator software/images while retaining the
build SDK and `adb`. Native removal options include:

- Android Studio > SDK Manager > SDK Tools > Android Emulator.
- `sdkmanager --sdk_root=<verified-sdk> --uninstall emulator`, when installed;
  consult local help for other/newer SDK CLIs.
- Device Manager or `avdmanager delete avd -n <approved-name>` for selected AVDs.

If package management is absent or unusable, a scoped fallback can remove the
verified self-contained `<sdk>/emulator` directory once no process uses it. Avoid
installing a new SDK or accepting setup-wizard downloads just to uninstall.

After removal, check retained `platform-tools/adb`, platforms, and build tools.
A stale UI inventory does not establish whether the files were removed.

## Project dependencies

The deep scan finds `node_modules` and `.build` in common project roots. Custom
worktrees or deeply nested packages may need a targeted search.

For `node_modules`, Pods, `.next`, Rust `target`, and other generated outputs,
check that the project is inactive, dependency locks/install steps exist, and no
wanted local modifications are stored there. Select individual paths for cleanup.
