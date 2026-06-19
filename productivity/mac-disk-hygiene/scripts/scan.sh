#!/usr/bin/env bash
# mac-disk-hygiene scanner — READ ONLY. Measures disk usage and surfaces
# reclaimable space. Never deletes anything. Safe to run anytime.
#
# Usage:
#   scan.sh            fast scan (no full-disk finds)
#   scan.sh --deep     also hunt node_modules / Python venvs (slower)
#
# Design notes for the model reading this output:
#   - Numbers are real du measurements (apparent disk usage, -x = stay on
#     one filesystem so we don't double-count mounts).
#   - The "KNOWN RECLAIMABLE" section lists targets that have a safe,
#     app-native reclaim command. Prefer those commands over `rm`.
#   - "DISCOVERY" drills into the parents that hide big stuff (Docker lives
#     inside Containers; tool data hides in dotdirs). Top-level du misses these.
#   - "ACCOUNTING" tells you how much used space is OUTSIDE home+/Applications
#     (i.e. system-level, needs sudo). Don't silently ignore it.

set -uo pipefail
DEEP=0
[[ "${1:-}" == "--deep" ]] && DEEP=1
HOME_DIR="${HOME}"

# human-readable from KB
hr() { awk -v k="$1" 'BEGIN{
  split("K M G T",u); s=k; i=1;
  while (s>=1024 && i<4){ s/=1024; i++ }
  printf "%6.1f %s", s, u[i]
}'; }

# measure a path in KB (apparent, one filesystem); echo "" if missing
sizek() { [[ -e "$1" ]] && du -skx "$1" 2>/dev/null | cut -f1 || echo ""; }

line() { printf '%s\n' "────────────────────────────────────────────────────────"; }

echo "MAC DISK HYGIENE SCAN — $(date '+%Y-%m-%d %H:%M')   (read-only)"
line

# ── OVERVIEW ────────────────────────────────────────────────────────────
echo "## OVERVIEW"
df -h / | sed 's/^/  /'
echo
# Real Data-volume numbers (df shows the sealed system volume on modern macOS)
diskutil info / 2>/dev/null | grep -iE "container total space|container free space|volume free space" | sed 's/^ */  /'
echo
echo "  Purgeable / local snapshots (df can show space as 'used' that is reclaimable):"
SNAPS=$(tmutil listlocalsnapshots / 2>/dev/null | grep -c 'com.apple')
echo "    APFS local snapshots: ${SNAPS:-0}  (reclaim: tmutil thinlocalsnapshots / <bytes> <urgency>)"
echo

# ── KNOWN RECLAIMABLE TARGETS ───────────────────────────────────────────
# Format: path|tier|reclaim-command
# tier: SAFE (regenerable cache) | APP (use the app's own cleanup) | CHECK (inspect first)
echo "## KNOWN RECLAIMABLE  (sorted by size; prefer the listed command over rm)"
TARGETS=(
  "$HOME_DIR/Library/Caches|SAFE|inspect subdirs; most are regenerable app caches"
  "$HOME_DIR/.npm/_cacache|SAFE|npm cache clean --force"
  "$HOME_DIR/.cache|SAFE|regenerable tool caches (inspect subdirs)"
  "$HOME_DIR/.bun/install/cache|SAFE|bun pm cache rm"
  "$HOME_DIR/Library/Caches/Homebrew|SAFE|brew cleanup --prune=all"
  "$HOME_DIR/Library/Caches/Yarn|SAFE|yarn cache clean"
  "$HOME_DIR/Library/pnpm/store|SAFE|pnpm store prune"
  "$HOME_DIR/Library/Developer/Xcode/DerivedData|SAFE|rm contents; Xcode rebuilds it"
  "$HOME_DIR/Library/Developer/Xcode/Archives|CHECK|old app archives — keep ones you may resubmit"
  "$HOME_DIR/Library/Developer/Xcode/iOS DeviceSupport|SAFE|delete old iOS version folders; Xcode re-downloads"
  "$HOME_DIR/Library/Developer/CoreSimulator/Devices|SAFE|xcrun simctl delete unavailable"
  "$HOME_DIR/Library/Developer/CoreSimulator/Caches|SAFE|simulator caches, regenerable"
  "$HOME_DIR/.gradle/caches|SAFE|gradle caches, regenerable"
  "$HOME_DIR/.nvm/versions|CHECK|old Node versions — nvm ls, then nvm uninstall <v>"
  "$HOME_DIR/Library/Containers/com.docker.docker|APP|docker system prune -a --volumes (or Docker Desktop > Troubleshoot > Purge data; uninstall if unused)"
  "$HOME_DIR/Library/Application Support/Code/Cache|SAFE|VS Code cache"
  "$HOME_DIR/Library/Application Support/Code/CachedData|SAFE|VS Code cached data"
  "$HOME_DIR/Library/Caches/Google|APP|Chrome cache — clear via Chrome or delete"
  "$HOME_DIR/.Trash|SAFE|empty Trash"
)
{
  for entry in "${TARGETS[@]}"; do
    p="${entry%%|*}"; rest="${entry#*|}"; tier="${rest%%|*}"; cmd="${rest#*|}"
    k=$(sizek "$p")
    [[ -z "$k" || "$k" -lt 51200 ]] && continue   # skip <50MB and missing
    printf '%d\t%s\t%s\t%s\n' "$k" "$tier" "$p" "$cmd"
  done
} | sort -rn | while IFS=$'\t' read -r k tier p cmd; do
  printf "  %s  [%-5s] %s\n             ↳ %s\n" "$(hr "$k")" "$tier" "${p/#$HOME_DIR/~}" "$cmd"
done
echo

# ── DISCOVERY: drill into the fat parents top-level du misses ────────────
echo "## DISCOVERY  (big items that hide inside parents — judge tier yourself)"
discover() {
  local parent="$1" n="${2:-6}"
  [[ -d "$parent" ]] || return
  echo "  ${parent/#$HOME_DIR/~}/*  (top $n):"
  du -shx "$parent"/* 2>/dev/null | sort -h | tail -"$n" | sed 's/^/    /'
}
discover "$HOME_DIR/Library/Containers" 6
discover "$HOME_DIR/Library/Application Support" 6
discover "$HOME_DIR/Library/Caches" 6
echo "  ~/.<dotdirs>  (top 8):"
du -shx "$HOME_DIR"/.[a-zA-Z]* 2>/dev/null | sort -h | tail -8 | sed 's/^/    /'
echo "  ~/* top-level dirs (top 8):"
du -shx "$HOME_DIR"/* 2>/dev/null | sort -h | tail -8 | sed 's/^/    /'
echo "  /Applications (top 6):"
du -shx /Applications/* 2>/dev/null | sort -h | tail -6 | sed 's/^/    /'
echo

# ── DEEP: heavy finds (opt-in) ──────────────────────────────────────────
if [[ "$DEEP" == "1" ]]; then
  echo "## DEEP  (node_modules in project roots — dormant projects are easy wins)"
  ROOTS=()
  for r in "$HOME_DIR/CODE" "$HOME_DIR/Projects" "$HOME_DIR/dev" "$HOME_DIR/src" "$HOME_DIR/work"; do
    [[ -d "$r" ]] && ROOTS+=("$r")
  done
  if [[ ${#ROOTS[@]} -gt 0 ]]; then
    find "${ROOTS[@]}" -maxdepth 4 -type d -name node_modules -prune 2>/dev/null | while read -r nm; do
      k=$(du -skx "$nm" 2>/dev/null | cut -f1); printf '%d\t%s\n' "${k:-0}" "$nm"
    done | sort -rn | head -15 | while IFS=$'\t' read -r k p; do
      printf "    %s  %s\n" "$(hr "$k")" "${p/#$HOME_DIR/~}"
    done
    echo "    ↳ delete node_modules in projects you're not actively building; reinstall with npm/yarn/pnpm install"
  else
    echo "    (no common project roots found — pass roots manually if needed)"
  fi
  echo
fi

# ── ACCOUNTING: how much lives outside home + /Applications ──────────────
echo "## ACCOUNTING"
USED_K=$(diskutil info / 2>/dev/null | awk -F'[()]' '/Container Free Space/{} /Container Total Space/{t=$2} /Container Free Space/{f=$2} END{}' )
TOTAL_BYTES=$(diskutil info / 2>/dev/null | awk -F'[()]' '/Container Total Space/{gsub(/[^0-9]/,"",$2); print $2; exit}')
FREE_BYTES=$(diskutil info / 2>/dev/null | awk -F'[()]' '/Container Free Space/{gsub(/[^0-9]/,"",$2); print $2; exit}')
HOME_K=$(du -skx "$HOME_DIR" 2>/dev/null | cut -f1)
APPS_K=$(du -skx /Applications 2>/dev/null | cut -f1)
if [[ -n "${TOTAL_BYTES:-}" && -n "${FREE_BYTES:-}" ]]; then
  USED_K=$(( (TOTAL_BYTES - FREE_BYTES) / 1024 ))
  ACCT_K=$(( ${HOME_K:-0} + ${APPS_K:-0} ))
  UNACCT_K=$(( USED_K - ACCT_K ))
  echo "  Used (Data volume):        $(hr "$USED_K")"
  echo "  ~/ (home):                 $(hr "${HOME_K:-0}")"
  echo "  /Applications:             $(hr "${APPS_K:-0}")"
  echo "  Outside home + apps:       $(hr "$UNACCT_K")   ← system-level, needs sudo to investigate"
  echo
  echo "  To probe system-level space, the user can run (will prompt for password):"
  echo "    sudo du -xhd 1 /System/Volumes/Data 2>/dev/null | sort -h | tail -15"
  echo "    sudo du -xhd 1 /private/var 2>/dev/null | sort -h | tail -10"
else
  echo "  (could not parse diskutil totals; skipping accounting)"
fi
echo
line
echo "Scan complete. Nothing was deleted. Hand this to the skill to build a ranked, tiered cleanup plan."
