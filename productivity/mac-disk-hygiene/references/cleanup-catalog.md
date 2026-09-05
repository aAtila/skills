# Cleanup catalog

Read the relevant section when classifying or removing a measured target.

- [Storage accounting and access](#storage-accounting-and-access)
- [Package-manager caches](#package-manager-caches)
- [Xcode and iOS simulators](#xcode-and-ios-simulators)
- [Docker engines and storage](#docker-engines-and-storage)
- [Browser caches and user content](#browser-caches-and-user-content)

For Swift build copies, agent-tool storage, and Android SDK components, see
[developer-storage.md](developer-storage.md).

## Storage accounting and access

On modern macOS, System and Data volumes share an APFS container. `df /` describes
the mounted System volume; use `df -k /System/Volumes/Data` consistently for cleanup
baselines and `diskutil info /` for container capacity/free space. The scanner
falls back to `/` on systems without the Data-volume mount.

`du` normally reports allocated blocks, not logical file length. Neither it nor a
file's logical size proves the space a deletion will recover:

- APFS clones can share blocks between a project's `.build` and an external cache.
- A sparse VM image can have a large logical capacity but occupy few host blocks.
- Mounted runtime contents are another view of a backing image. Do not add both.
- Docker images can share layers. Prefer the engine's reclaimable estimate.
- Snapshots, retained downloads, deferred deletion, and concurrent writes can alter
  the observed free-space change. A shortfall alone does not identify its cause.

Record before/after free space in one unit, preferably bytes or KiB, then convert
for display. Do not attribute changes elsewhere in the session to one cleanup.

A failed `diskutil`, `tmutil`, or simulator query is unknown. Sandbox restrictions
can prevent service access; a scoped read-only retry with authorized host access
can distinguish that from an application failure. Permission denied does not by
itself establish SIP protection. Never defeat SIP or manually purge protected
system assets.

`tmutil listlocalsnapshots /` inventories Time Machine local snapshots only. If
snapshot cleanup is actually warranted and approved, consult `tmutil help` before
using `thinlocalsnapshots`; do not prescribe thinning solely because `du` and free
space differ.

The scanner's outside-home/apps figure is a rough accounting residual, not a list
of disposable system files. It includes other volumes, unreadable paths, shared
storage, and system-managed data. Optional read-only probes, when authorized:

```bash
sudo du -xhd 1 /System/Volumes/Data 2>/dev/null | sort -h | tail -15
sudo du -xhd 1 /Library 2>/dev/null | sort -h | tail -10
sudo du -xhd 1 /private/var 2>/dev/null | sort -h | tail -10
```

Those suppressed errors make the results partial; report that limitation. Leave
swap/sleep state and unidentified system storage to macOS.

## Package-manager caches

Measure the configured cache location. Use only commands for installed tools.

| Candidate | Preferred cleanup after approval |
|---|---|
| npm content cache | `npm cache clean --force` |
| Yarn | `yarn cache clean` |
| pnpm store | `pnpm store prune` |
| Bun | `bun pm cache rm` |
| Homebrew | Preview `brew cleanup --prune=all --dry-run`, then `brew cleanup --prune=all` |
| CocoaPods | `pod cache clean --all` |
| Go build cache | `go clean -cache` |
| Gradle caches | Remove the selected cache directory after builds/daemons using it have stopped |
| pip cache | `python3 -m pip cache purge`, if this is the environment owning the cache |

Treat `brew autoremove` as a separate package-removal decision. Installed Node
versions also need inspection: check project pins, current/default versions, and
then use `nvm uninstall <approved-version>`.

For a cache command that fails because of cwd or missing tooling, verify the exact
cache path before considering scoped removal. Avoid deleting all of `~/.cache`,
`~/.npm`, or `~/Library/Caches` without inspecting their contents.

## Xcode and iOS simulators

Distinguish these targets before estimating savings:

| Target | Discovery and consequence |
|---|---|
| DerivedData | Build products and downloaded packages; recreatable, but the next build can be expensive. Check for active builds. |
| Archives | Release archives/symbols may be needed later. Select individually. |
| DeviceSupport | Inspect version folders; retain versions needed for current physical-device development. |
| Simulator devices | Installed test apps, settings, and saved device data. Removal loses that state. |
| Simulator runtimes | Shared OS images supporting devices; removal requires a later download to run that OS. |

Use the installed tool's help and live inventory:

```bash
xcrun simctl list devices --json
xcrun simctl list devices unavailable
xcrun simctl runtime list --json
```

`xcrun simctl delete unavailable` deletes unavailable **devices**. The total size of
`CoreSimulator/Devices` is not the size reclaimable by that command, and it does
not uninstall shared runtimes. Unavailable device state may still matter to the
user; it is not an ordinary cache.

For specifically approved targets:

```bash
xcrun simctl delete <device-uuid>
xcrun simctl runtime delete <runtime-image-identifier>
```

Use the identifier from the relevant inventory, not a remembered UUID. Check for
booted devices and explain any required shutdown. Avoid blanket `erase all` or
runtime deletion when the user selected one device.

Runtime verification has two parts: inventory removal and actual host-space
recovery. An observed iOS runtime uninstall left a MobileAsset download under
`/System/Library/AssetsV2` even though `simctl` listed no runtimes. Treat retained
assets as an explicit unresolved storage condition; do not claim the full image
size was freed or provide a raw deletion recipe for that protected location.

## Docker engines and storage

First establish which engine the user uses. Docker Desktop, Colima, and other
engines can retain separate VM disks on the same Mac.

```bash
docker context ls
docker context show
docker --context <chosen-context> system df -v
docker --context <chosen-context> ps -a
docker --context <chosen-context> image ls -a
docker --context <chosen-context> volume ls
```

Keep the explicit context on every mutation. A stopped engine may need the user
to start its app before inventory is possible. A failure in one engine is not
proof that another engine is broken. Real VM I/O errors are a reason to stop
pruning that engine and discuss diagnosis, not reset it or delete its disk image.

Compare `ls -lh` logical VM capacity with `du -h` allocated host storage. Inventory
containers and their mounts before proposing image or volume removal. An image
with zero container references may still be used for future builds or tests;
retain versions the user says they need.

Prefer selected removal:

```bash
docker --context <chosen-context> image rm <approved-image-id-or-tag>
```

Do not force removal when Docker reports a reference. A stopped container can
hold wanted state and keep an image in use. Inspect build cache separately; if
nonzero and approved, use the engine's supported builder cleanup.

Broad `system prune -a --volumes` is not the default recipe. Check the installed
command's help: current `system prune --volumes` targets anonymous volumes, while
`volume prune --all` also includes named volumes. **Both kinds can hold real
database data**, and zero links does not establish disposability.

After cleanup, verify the selected images are gone, retained images/containers
remain, and host free space changed. Internal Docker savings need not immediately
match host-file shrinkage. Disk reset, purge-data UI, or uninstalling an engine is
a separate destructive scope.

## Browser caches and user content

Clear browser cached images/files through the browser when practical. Preserve
cookies, passwords, history, profiles, and site data unless specifically approved.
Inspect `~/Library/Caches/Google` for ownership instead of equating all Google
storage with one browser cache.

Downloads and Trash are CHECK targets; neither is inherently regenerable. Inspect
before deleting or emptying them. Photos, Mail, Messages, application databases,
and agent conversation history should be managed through their owning apps.

Model weights such as FluidAudio, Hugging Face, or Ollama downloads are CHECK
items even inside a cache directory. Verify which application needs them and
explain the download cost before removal.
