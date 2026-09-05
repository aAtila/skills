#!/usr/bin/env bash
# Read-only disk discovery. Sizes are allocated blocks, not guaranteed recovery.
# Usage: bash scan.sh [--deep]
set -uo pipefail

hr() {
  awk -v k="$1" 'BEGIN {
    split("KiB MiB GiB TiB", u); i=1
    while (k>=1024 && i<4) { k/=1024; i++ }
    printf "%.1f %s", k, u[i]
  }'
}

# Only leaf candidates go in this table. Parent totals are discovery, never added.
candidate() {
  local p="$1" tier="$2" action="$3" measured k
  [[ -e "$p" ]] || return 0
  if measured=$(du -skx "$p" 2>/dev/null); then
    k=$(printf '%s\n' "$measured" | awk 'NR==1 {print $1}')
    if [[ "$k" =~ ^[0-9]+$ ]]; then
      (( k < 51200 )) || printf '%s\t%s\t%s\t%s\n' "$k" "$tier" "$p" "$action"
    else
      printf '  Unknown size: %s\n' "$p" >&2
    fi
  else
    printf '  Unknown/partial size (read failed): %s\n' "$p" >&2
  fi
}

# One traversal provides the immediate children and the parent total.
# Expose incomplete reads instead of presenting partial accounting as exact.
LAST_TOTAL_K=''
discover() {
  local parent="$1" limit="${2:-8}" measured complete=1
  LAST_TOTAL_K=''
  [[ -d "$parent" ]] || return 0
  echo "  $parent (largest immediate children; not additional reclaimable totals):"
  measured=$(du -kxd 1 "$parent" 2>/dev/null) || complete=0
  printf '%s\n' "$measured" | awk -F '\t' -v p="$parent" '$2 != p && $1 ~ /^[0-9]+$/ {print}' |
    sort -rn | head -n "$limit" |
    while IFS=$'\t' read -r k path; do
      printf '    %10s  %s\n' "$(hr "$k")" "$path"
    done
  if (( complete )); then
    LAST_TOTAL_K=$(printf '%s\n' "$measured" | awk -F '\t' -v p="$parent" '$2 == p {print $1}')
  else
    echo '    Partial listing: some paths could not be read.'
  fi
}

scan() {
  local HOME_DIR="$1" DEEP="$2"
  local DATA_VOLUME=/System/Volumes/Data
  [[ -d "$DATA_VOLUME" ]] || DATA_VOLUME=/
  printf 'MAC DISK HYGIENE SCAN - %s (read-only)\n' "$(date '+%Y-%m-%d %H:%M')"
  echo '## OVERVIEW'
  df -k "$DATA_VOLUME"
  DISK_INFO=''
  if DISK_INFO=$(diskutil info / 2>/dev/null); then
    printf '%s\n' "$DISK_INFO" | awk '/Container Total Space|Container Free Space/ {print}'
  else
    echo '  APFS container information unavailable; use the df baseline above.'
  fi
  if SNAPSHOTS=$(tmutil listlocalsnapshots / 2>/dev/null); then
    SNAP_COUNT=$(printf '%s\n' "$SNAPSHOTS" | awk '/^com\.apple\.TimeMachine\./ {n++} END {print n+0}')
    echo "  Time Machine local snapshots: $SNAP_COUNT (not all APFS snapshots)."
  else
    echo '  Time Machine local snapshots: unknown (query failed).'
  fi

  echo
  echo '## CANDIDATES (measured size, not a deletion plan or guaranteed recovery)'
  {
    candidate "$HOME_DIR/.npm/_cacache" SAFE 'npm cache clean --force'
    candidate "$HOME_DIR/.npm/_npx" CHECK 'verify temporary packages and active commands; scoped removal'
    candidate "$HOME_DIR/.cache/codex-runtimes" CHECK 'verify runtime ownership and active use; see developer-storage.md'
    candidate "$HOME_DIR/.bun/install/cache" SAFE 'bun pm cache rm'
    candidate "$HOME_DIR/Library/Caches/Homebrew" SAFE 'brew cleanup --prune=all --dry-run, then approved cleanup'
    candidate "$HOME_DIR/Library/Caches/Yarn" SAFE 'yarn cache clean'
    candidate "$HOME_DIR/Library/Caches/org.swift.swiftpm" SAFE 'shared Swift cache; check active builds before scoped removal'
    candidate "$HOME_DIR/Library/pnpm/store" SAFE 'pnpm store prune'
    candidate "$HOME_DIR/Library/Developer/Xcode/DerivedData" SAFE 'check active builds; remove selected build outputs'
    candidate "$HOME_DIR/Library/Developer/Xcode/Archives" CHECK 'inspect release archives and symbols'
    candidate "$HOME_DIR/Library/Developer/Xcode/iOS DeviceSupport" CHECK 'select versions after checking physical-device needs'
    candidate "$HOME_DIR/Library/Developer/CoreSimulator/Devices" CHECK 'simctl device inventory; total is NOT unavailable-device reclaim'
    candidate "$HOME_DIR/Library/Developer/CoreSimulator/Caches" CHECK 'verify cache ownership and simulator activity'
    candidate "$HOME_DIR/.gradle/caches" SAFE 'check active builds/daemons; scoped cache removal'
    candidate "$HOME_DIR/.nvm/versions" CHECK 'check project pins and active versions; nvm uninstall selected version'
    candidate "$HOME_DIR/Library/Containers/com.docker.docker" APP 'Docker Desktop store; choose context and inventory images/volumes first'
    candidate "$HOME_DIR/.colima" APP 'separate Colima VM store; choose context and inventory first'
    candidate "$HOME_DIR/Library/Application Support/RepoPrompt CE/Conductor/BuildCache" APP 'conductor cache status; drop approved keys; see developer-storage.md'
    candidate "$HOME_DIR/.claude/telemetry" CHECK 'inspect failed-event file set; preserve history; see developer-storage.md'
    candidate "$HOME_DIR/Library/Application Support/Code/Cache" SAFE 'verified VS Code cache; scoped cleanup'
    candidate "$HOME_DIR/Library/Application Support/Code/CachedData" SAFE 'verified VS Code cached data; scoped cleanup'
    candidate "$HOME_DIR/Library/Caches/Google" APP 'inspect owner; browser cached images/files cleanup'
    candidate "$HOME_DIR/.Trash" CHECK 'inspect user content; explicit approval to empty'

    ANDROID_SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME_DIR/Library/Android/sdk}}"
    ANDROID_AVDS="${ANDROID_AVD_HOME:-${ANDROID_USER_HOME:-$HOME_DIR/.android}/avd}"
    candidate "$ANDROID_AVDS" CHECK 'Android virtual-device state; list/select AVDs first'
    candidate "$ANDROID_SDK/system-images" APP 'Android runtime downloads; SDK Manager removal after selection'
    candidate "$ANDROID_SDK/emulator" APP 'emulator program; preserve adb/build SDK; SDK Manager uninstall'
  } | sort -rn | while IFS=$'\t' read -r k tier path action; do
    printf '  %10s [%s] %s\n    %s\n' "$(hr "$k")" "$tier" "$path" "$action"
  done
  echo '  No candidate sum: approval, shared blocks, and target overlap require review.'
  echo '  Inventory shared iOS runtimes separately with: xcrun simctl runtime list --json'
  echo '  Verify configured Android paths; project/IDE overrides may differ from these defaults.'

  echo
  echo '## DISCOVERY (inspect large parents; never delete them wholesale)'
  discover "$HOME_DIR/Library/Containers" 6
  discover "$HOME_DIR/Library/Application Support" 8
  discover "$HOME_DIR/Library/Caches" 8
  discover "$HOME_DIR/.cache" 6
  discover "$HOME_DIR" 12
  HOME_K="$LAST_TOTAL_K"
  discover /Applications 6
  APPS_K="$LAST_TOTAL_K"

  if (( DEEP )); then
    echo
    echo '## DEEP (CHECK: project dependencies and Swift build outputs)'
    ROOTS=()
    for root in "$HOME_DIR/CODE" "$HOME_DIR/Projects" "$HOME_DIR/dev" "$HOME_DIR/src" "$HOME_DIR/work"; do
      [[ ! -d "$root" ]] || ROOTS+=("$root")
    done
    if (( ${#ROOTS[@]} )); then
      # Keep find errors visible. Prune matches so their internals are not counted again.
      find "${ROOTS[@]}" -maxdepth 5 -type d \( -name node_modules -o -name .build \) -prune -print0 |
        while IFS= read -r -d '' path; do
          candidate "$path" CHECK 'verify project/activity and cleanup target'
        done | sort -rn | head -n 15 |
        while IFS=$'\t' read -r k tier path action; do
          printf '  %10s [%s] %s\n' "$(hr "$k")" "$tier" "$path"
        done
    else
      echo '  No common project roots found; inspect user-specified roots if relevant.'
    fi
  fi

  echo
  echo '## ACCOUNTING (rough residual, not reclaimable storage)'
  TOTAL_BYTES=$(printf '%s\n' "$DISK_INFO" | awk -F '[()]' '/Container Total Space/ {gsub(/[^0-9]/,"",$2); print $2; exit}')
  FREE_BYTES=$(printf '%s\n' "$DISK_INFO" | awk -F '[()]' '/Container Free Space/ {gsub(/[^0-9]/,"",$2); print $2; exit}')
  if [[ "$TOTAL_BYTES" =~ ^[0-9]+$ && "$FREE_BYTES" =~ ^[0-9]+$ && "$HOME_K" =~ ^[0-9]+$ && "$APPS_K" =~ ^[0-9]+$ ]]; then
    USED_K=$(( (TOTAL_BYTES - FREE_BYTES) / 1024 ))
    RESIDUAL_K=$(( USED_K - HOME_K - APPS_K ))
    printf '  APFS container used: %s\n  Readable home: %s\n  Applications: %s\n' "$(hr "$USED_K")" "$(hr "$HOME_K")" "$(hr "$APPS_K")"
    printf '  Container used minus home/apps: %s\n' "$(hr "$RESIDUAL_K")"
    echo '  Different accounting scopes and shared blocks make this approximate; it is not all system junk.'
  else
    echo '  Unavailable: container totals or complete home/apps measurements could not be read.'
  fi
  echo '  For unexplained usage, see the scoped system probes in references/cleanup-catalog.md.'
  echo
  echo 'Scan complete. Nothing was deleted. Review ownership, consequences, and scope before cleanup.'
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
case "${1:-}" in
  '') DEEP=0 ;;
  --deep) DEEP=1 ;;
  -h|--help) echo 'Usage: bash scan.sh [--deep]'; exit 0 ;;
  *) echo "Unknown option: $1" >&2; exit 2 ;;
esac
  scan "$HOME" "$DEEP"
fi
