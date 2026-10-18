#!/usr/bin/env python3
"""Read-only scan of space left behind by development work in $HOME.

Measures sizes only (du, stat, directory names, and the tools' own status
commands); never opens file contents and never deletes anything. Reads the
history CSV first, writes report.html, then appends this run to the history.

Usage: python3 scan.py [--min-mb 50] [--out ~/disk-report]
Python 3.9 compatible (macOS /usr/bin/python3).
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HOME = os.path.expanduser("~")
LIB = os.path.join(HOME, "Library")
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "report-template.html")

# History schema is shared across runs: changing these columns orphans every earlier scan.
CSV_COLUMNS = ["scanned_at", "id", "group", "kind", "kib"]
GROW_KIB, GROW_PCT = 10 * 1024, 0.02          # flagged only when both are exceeded
UNKNOWN_MIN_KIB = 500 * 1024                  # unrecognised folders listed from this size
MAX_DEPTH = 10

# Kinds that always land in "let me review first".
REVIEW_KINDS = {"session", "model", "docker", "runtime", "device", "worktree", "unknown"}

# Never entered by the home walk: permission-prompting (TCC) folders, Photos, iCloud,
# Trash, and ~/Library (reached only through the catalog and the sweep roots below).
PRUNE_TOP = {"Library", "Desktop", "Documents", "Downloads", "Pictures", "Movies",
             "Music", "Public", "Applications", ".Trash"}
PROTECTED_NOTE = [
    "~/Desktop, ~/Documents, ~/Downloads (permission prompt)",
    "~/Pictures (includes the Photos library), ~/Movies, ~/Music",
    "~/Library/Mobile Documents and ~/Library/CloudStorage (iCloud and cloud drives)",
    "~/Library/Containers and Group Containers (other apps' data; Docker Desktop and OrbStack are sized through docker)",
    "~/Library/Mail, Messages, Safari and other Apple app data", "~/.Trash",
    "Other volumes: external drives, disk images, network shares",
]
# Sweep roots: each child folder no catalog entry claims is listed as unrecognised when big.
SWEEP_ROOTS = [
    (os.path.join(HOME, ".cache"), "Tool cache with no catalog entry. Usually rebuilt by its tool; check which tool owns it first.",
     "Find the owning tool and use its cleanup, or delete the folder in Finder once you know it's a cache."),
    (os.path.join(HOME, ".local", "share"), "Tool data with no catalog entry. May hold sessions, settings or downloads.",
     "Find the owning tool and use its cleanup."),
    (os.path.join(LIB, "Caches"), "App cache with no catalog entry. Usually rebuilt by its app; check which app owns it first.",
     "Quit the owning app, then delete the folder in Finder."),
    (os.path.join(LIB, "Application Support"), "App data with no catalog entry. May hold settings, sessions, models or downloads.",
     "Remove what you don't need from the owning app's settings, or quit it and delete the folder in Finder."),
]
DOTDIR_NOTE = ("Unrecognised tool data in your home folder. Find out which tool owns it before removing.",
               "Find the owning tool and use its cleanup.")
# Apple-owned or permission-prompting children of the Library sweep roots.
SWEEP_SKIP = {"AddressBook", "CallHistoryDB", "CallHistoryTransactions", "CloudDocs", "CloudKit",
              "DifferentialPrivacy", "FaceTime", "FileProvider", "Knowledge", "MobileSync", "Safari"}

NVM = '. "${NVM_DIR:-$HOME/.nvm}/nvm.sh"'
VCS_DIRS = {".git", ".hg", ".svn"}


def home(p):
    return os.path.join(HOME, p)


def tilde(p):
    return "~" + p[len(HOME):] if p == HOME or p.startswith(HOME + "/") else p


def q(s):
    return shlex.quote(s)


def sh(args, timeout=60):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def du_kib(path):
    """(KiB, None) or (None, reason). macOS refuses protected folders silently with EPERM."""
    try:
        r = subprocess.run(["du", "-skx", path], capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return None, "timed out"
    m = re.match(r"(\d+)", r.stdout)
    if m:
        return int(m.group(1)), None
    return None, "protected by macOS" if "not permitted" in r.stderr else "could not measure"


def entry(path, title, kind, consequence, cmd=None, manual=None, group=None, **extra):
    """One report item. Every item carries a clean command or manual instructions, never a raw rm."""
    if group is None:
        group = "review" if kind in REVIEW_KINDS else "safe"
    assert kind not in REVIEW_KINDS or group == "review", path
    assert cmd or manual, path
    it = {"path": path, "id": tilde(path) if path else None, "display": tilde(path) if path else None,
          "title": title, "kind": kind, "group": group, "consequence": consequence,
          "cmd": cmd, "manual": manual, "touched": None}
    it.update(extra)
    return it


def catalog():
    A, C = os.path.join(LIB, "Application Support"), os.path.join(LIB, "Caches")
    X = os.path.join(LIB, "Developer")
    quit_delete = "No clean command. Quit %s, then delete the folder in Finder."
    return [
        # --- safe: regenerable caches
        entry(home(".npm/_cacache"), "npm cache", "cache", "npm re-downloads packages on the next install. Projects aren't affected.", "npm cache clean --force"),
        entry(home("Library/pnpm/store"), "pnpm store", "cache", "Only packages no project references are pruned, so it may free less than shown.", "pnpm store prune"),
        entry(home(".local/share/pnpm/store"), "pnpm store", "cache", "Only packages no project references are pruned, so it may free less than shown.", "pnpm store prune"),
        entry(os.path.join(C, "Yarn"), "Yarn cache", "cache", "Yarn re-downloads packages on the next install.", "yarn cache clean"),
        entry(home(".yarn/berry/cache"), "Yarn Berry cache", "cache", "Yarn re-downloads packages on the next install.", "yarn cache clean --mirror"),
        entry(home(".bun/install/cache"), "Bun cache", "cache", "Bun re-downloads packages on the next install.", "bun pm cache rm"),
        entry(home(".nvm/.cache"), "nvm download cache", "cache", "nvm re-downloads the Node tarball the next time you install a version.", NVM + " && nvm cache clear"),
        entry(os.path.join(C, "pip"), "pip cache", "cache", "pip re-downloads wheels on the next install.", "python3 -m pip cache purge"),
        entry(home(".cache/uv"), "uv cache", "cache", "uv re-downloads packages and Python builds when needed.", "uv cache clean"),
        entry(os.path.join(C, "go-build"), "Go build cache", "cache", "The next Go builds run slower once while the cache refills.", "go clean -cache"),
        entry(home("go/pkg/mod"), "Go module cache", "cache", "Go modules re-download on the next build.", "go clean -modcache"),
        entry(home(".cargo/registry"), "Cargo registry", "cache", "Crates re-download on the next cargo build.",
              manual="Cargo has no built-in clean: `cargo install cargo-cache && cargo cache --autoclean`, or delete the folder in Finder."),
        entry(home(".gradle/caches"), "Gradle caches", "cache", "Dependencies re-download and the next builds run slower.",
              manual="Run `gradle --stop`, then delete the folder in Finder."),
        entry(home(".m2/repository"), "Maven repository", "cache", "Maven re-downloads dependencies on the next build.",
              manual="No clean command. Delete the folder in Finder."),
        entry(os.path.join(C, "org.swift.swiftpm"), "SwiftPM shared cache", "cache", "Package checkouts re-download on the next resolve.", "swift package purge-cache"),
        entry(os.path.join(C, "CocoaPods"), "CocoaPods cache", "cache", "Pods re-download on the next pod install.", "pod cache clean --all"),
        entry(os.path.join(C, "Homebrew"), "Homebrew downloads", "cache", "Old bottles and downloads go. Installed software isn't affected.", "brew cleanup --prune=all"),
        entry(home(".cache/pre-commit"), "pre-commit environments", "cache", "Hook environments rebuild on the next commit.", "pre-commit clean"),
        entry(os.path.join(C, "ms-playwright"), "Playwright browsers", "cache", "Browsers re-download on the next `playwright install`.", "npx playwright uninstall --all"),
        entry(home(".cache/puppeteer"), "Puppeteer browsers", "cache", "Chrome for Testing re-downloads on the next puppeteer install.",
              'npx @puppeteer/browsers clear --path "$HOME/.cache/puppeteer"'),
        entry(os.path.join(C, "node-gyp"), "node-gyp headers", "cache", "Node headers re-download on the next native module build.",
              manual="Run `npx node-gyp list`, then `npx node-gyp remove <version>` for each version."),
        entry(os.path.join(X, "Xcode/DerivedData"), "Xcode DerivedData", "cache", "Xcode rebuilds and re-indexes each project on next open.",
              manual=quit_delete % "Xcode"),
        entry(os.path.join(X, "Xcode/iOS DeviceSupport"), "Xcode device symbols", "cache",
              "Xcode re-copies symbols the next time each device connects, which takes minutes per device.",
              manual="No clean command. Delete folders for iOS versions you no longer debug, in Finder."),
        entry(os.path.join(C, "JetBrains"), "JetBrains caches", "cache", "JetBrains IDEs re-index on next open.",
              manual="In the IDE, choose File → Invalidate Caches, or quit it and delete the folder in Finder."),
        entry(os.path.join(A, "Code/CachedExtensionVSIXs"), "VS Code extension downloads", "cache", "Old extension installers go. Installed extensions aren't affected.",
              manual=quit_delete % "VS Code"),
        entry(os.path.join(A, "Code/CachedData"), "VS Code cached data", "cache", "VS Code rebuilds it on next start.", manual=quit_delete % "VS Code"),
        entry(os.path.join(A, "Code/Cache"), "VS Code web cache", "cache", "VS Code rebuilds it on next start.", manual=quit_delete % "VS Code"),
        entry(os.path.join(A, "Cursor/CachedData"), "Cursor cached data", "cache", "Cursor rebuilds it on next start.", manual=quit_delete % "Cursor"),
        entry(os.path.join(A, "Cursor/Cache"), "Cursor web cache", "cache", "Cursor rebuilds it on next start.", manual=quit_delete % "Cursor"),
        # --- review: caches with side effects
        entry(home(".npm/_npx"), "npx package cache", "cache",
              "Tools started with npx (including many MCP servers) re-download on next launch; ones running now may break.",
              manual="npm has no command for this. Quit agents and MCP clients, then delete the folder in Finder.", group="review"),
        # --- review: runtimes and devices
        entry(os.path.join(LIB, "Android/sdk"), "Android SDK", "runtime", "Removed SDK components must be reinstalled before Android builds work.",
              manual="Run `sdkmanager --list_installed`, then `sdkmanager --uninstall <package>`, or use Android Studio's SDK Manager."),
        entry(os.path.join(X, "CoreSimulator/Devices"), "iOS simulators", "device",
              "Only simulators whose runtime is gone are deleted. Others keep their apps and data.", "xcrun simctl delete unavailable"),
        entry(home(".android/avd"), "Android emulators", "device", "Deleted emulators lose their installed apps and data.",
              manual="Run `emulator -list-avds`, then `avdmanager delete avd -n <name>`."),
        entry(os.path.join(X, "Xcode/Archives"), "Xcode archives", "device",
              "Archived builds and their dSYMs go; crash reports from those releases can no longer be symbolicated.",
              manual="Delete old archives in Xcode → Window → Organizer."),
        # --- review: models
        entry(home(".ollama/models"), "Ollama models", "model", "Pulled models are gone; `ollama pull` gets them back (often several GB each).",
              manual="Run `ollama list`, then `ollama rm <model>`."),
        entry(home(".cache/huggingface"), "Hugging Face cache", "model", "Models and datasets re-download on next use.",
              manual="Run `hf cache delete` (older installs: `huggingface-cli delete-cache`) and pick what to remove."),
        entry(home(".lmstudio/models"), "LM Studio models", "model", "Models must be downloaded again.", manual="Remove them in LM Studio → My Models."),
        entry(home(".cache/lm-studio/models"), "LM Studio models", "model", "Models must be downloaded again.", manual="Remove them in LM Studio → My Models."),
        # --- review: sessions
        entry(home(".claude/projects"), "Claude Code sessions", "session", "You lose `claude --resume` history and per-project memory.",
              manual='Let Claude Code prune old transcripts: set "cleanupPeriodDays" in ~/.claude/settings.json.'),
        entry(home(".codex/sessions"), "Codex CLI sessions", "session", "You lose `codex resume` history.",
              manual="No clean command. Archive or delete old year/month folders yourself."),
        entry(os.path.join(A, "Code/User/workspaceStorage"), "VS Code workspace state", "session",
              "VS Code loses per-workspace state, including extension chat history.", manual=quit_delete % "VS Code"),
        entry(os.path.join(A, "Cursor/User/workspaceStorage"), "Cursor workspace state", "session",
              "Cursor loses per-workspace state, including chat history.", manual=quit_delete % "Cursor"),
        # --- review: container VMs stored as plain folders (engines are sized through docker)
        entry(home(".colima/_lima"), "Colima VM", "docker",
              "Deletes the Colima VM and every image, container and volume inside it; overlaps the docker (colima) items.", "colima delete -f"),
    ]


def runtime_items():
    out = []
    nvm_dir = home(".nvm/versions/node")
    if os.path.isdir(nvm_dir):
        default = sh(["bash", "-c", NVM + " >/dev/null 2>&1 && nvm version default"])
        for v in sorted(os.listdir(nvm_dir)):
            p = os.path.join(nvm_dir, v)
            if v.startswith("v") and os.path.isdir(p) and not os.path.islink(p) and v != default:
                note = "" if default else " Couldn't tell which version is your nvm default."
                out.append(entry(p, "Node %s (nvm)" % v, "runtime",
                                 "Projects pinned to this version (.nvmrc) need `nvm install` again; its global npm packages go with it." + note,
                                 NVM + " && nvm uninstall " + v))
    pyenv_dir = home(".pyenv/versions")
    if os.path.isdir(pyenv_dir):
        pyenv = shutil.which("pyenv") or home(".pyenv/bin/pyenv")
        globals_ = set((sh([pyenv, "global"]) or "").split())
        for v in sorted(os.listdir(pyenv_dir)):
            p = os.path.join(pyenv_dir, v)
            if os.path.isdir(p) and not os.path.islink(p):
                note = " It's your pyenv global." if v in globals_ else ""
                out.append(entry(p, "Python %s (pyenv)" % v, "runtime",
                                 "Virtualenvs and tools built on it stop working." + note, "pyenv uninstall -f " + q(v)))
    rust_dir = home(".rustup/toolchains")
    if os.path.isdir(rust_dir):
        default = ((sh(["rustup", "default"]) or "").split() or [None])[0]
        for t in sorted(os.listdir(rust_dir)):
            p = os.path.join(rust_dir, t)
            if os.path.isdir(p) and not os.path.islink(p) and t != default:
                out.append(entry(p, "Rust %s" % t, "runtime", "Projects pinned to this toolchain must reinstall it.",
                                 "rustup toolchain uninstall " + q(t)))
    return out


# Build output, keyed by folder name: (group, markers relative to the project dir, needs a git repo, consequence).
# markers=None means any; a marker inside the folder (".venv/pyvenv.cfg") confirms what it is.
PKG = ("package.json",)
ARTIFACTS = {
    ".next": ("safe", PKG, False, "Next.js build cache. The next `next dev` or `next build` recreates it, slower the first time."),
    ".turbo": ("safe", ("package.json", "turbo.json"), False, "Turborepo task cache. The next run does full builds instead of cache hits."),
    ".nuxt": ("safe", PKG, False, "Nuxt build output. Recreated on the next build or dev run."),
    ".output": ("safe", PKG, False, "Nuxt/Nitro build output. Recreated on the next build."),
    ".svelte-kit": ("safe", PKG, False, "SvelteKit build output. Recreated on the next build or dev run."),
    ".parcel-cache": ("safe", PKG, False, "Parcel cache. The next build runs uncached once."),
    ".expo": ("safe", PKG, False, "Expo's local cache and dev-server state. Recreated on the next `expo start`."),
    ".build": ("safe", ("Package.swift",), False, "SwiftPM build products and checkouts. The next build re-resolves and recompiles from scratch."),
    "target": ("safe", ("Cargo.toml",), False, "Rust build output. The next cargo build recompiles everything."),
    "DerivedData": ("safe", None, False, "Xcode build output. Xcode rebuilds the project."),
    "node_modules": ("review", PKG, False, "The project won't run or build until you reinstall dependencies; hand-patched packages are lost."),
    "Pods": ("review", ("Podfile",), False, "CocoaPods dependencies. Run `pod install` before the next build."),
    ".venv": ("review", (".venv/pyvenv.cfg",), False, "Python virtualenv. Recreate it and reinstall packages before running the project."),
    "venv": ("review", ("venv/pyvenv.cfg",), False, "Python virtualenv. Recreate it and reinstall packages before running the project."),
    "build": ("review", None, True, "Compiled output, rebuilt by the build script. Check it isn't the only copy of something you shipped."),
    "dist": ("review", None, True, "Compiled output, rebuilt by the build script. Check it isn't the only copy of something you shipped."),
}

_repo_cache = {}


def find_repo(d):
    """Nearest ancestor (inside $HOME) holding .git, or None. Worktrees count: their .git is a file."""
    if d in _repo_cache:
        return _repo_cache[d]
    a, found = d, None
    while a.startswith(HOME + "/"):
        if os.path.exists(os.path.join(a, ".git")):
            found = a
            break
        a = os.path.dirname(a)
    _repo_cache[d] = found
    return found


def artifact_entry(path, parent, name, repo):
    group, _, _, consequence = ARTIFACTS[name]
    proj = repo or parent
    title = name + " · " + os.path.basename(proj) + ("" if proj == parent else "/" + os.path.relpath(parent, proj))
    if name == ".build" and os.path.exists(os.path.join(parent, "Package.swift")):
        cmd = "swift package --package-path %s reset" % q(parent)
    elif name == "target" and os.path.exists(os.path.join(parent, "Cargo.toml")):
        cmd = "cargo clean --manifest-path %s" % q(os.path.join(parent, "Cargo.toml"))
    elif repo:
        cmd = "git -C %s clean -fdX -- %s" % (q(repo), q(os.path.relpath(path, repo)))  # git-ignored files only
    else:
        cmd = None
    manual = None if cmd else (
        "Quit Xcode, then delete the folder in Finder." if name == "DerivedData"
        else "Not in a git repo and the tool has no clean command. Delete it in Finder if you're sure.")
    return entry(path, title, "project", consequence, cmd, manual, group=group, project=proj)


def local_dir(e, dev):
    try:
        return e.is_dir(follow_symlinks=False) and e.stat(follow_symlinks=False).st_dev == dev
    except OSError:
        return False


def walk_home(dev, skipped):
    """Find build output and git repos under $HOME without entering protected or other-volume folders."""
    hits, repos = [], []
    stack = [(HOME, 0)]
    while stack:
        d, depth = stack.pop()
        try:
            entries = list(os.scandir(d))
        except PermissionError:
            skipped.append(tilde(d) + " (permission denied)")
            continue
        except OSError:
            continue
        if depth > 0 and any(e.name == ".git" and local_dir(e, dev) for e in entries):
            repos.append(d)
        for e in entries:
            name = e.name
            if name in VCS_DIRS or not local_dir(e, dev):
                continue
            if depth == 0 and (name in PRUNE_TOP or name.startswith(".")):
                continue
            spec = ARTIFACTS.get(name)
            if spec is not None:
                _, markers, needs_repo, _ = spec
                repo = find_repo(d)
                if (markers is None or any(os.path.exists(os.path.join(d, m)) for m in markers)) and (repo or not needs_repo):
                    hits.append(artifact_entry(e.path, d, name, repo))
                    continue
            if name.startswith(".") or depth >= MAX_DEPTH:
                continue
            stack.append((e.path, depth + 1))
    return hits, repos


def protected(p):
    rel = os.path.relpath(p, HOME)
    if rel.startswith(".."):
        return True
    top = rel.split(os.sep)[0]
    if top == "Library":
        parts = rel.split(os.sep)
        return len(parts) < 2 or parts[1] not in ("Application Support", "Caches", "Developer")
    return top in PRUNE_TOP


def worktree_items(repos, dev):
    out, seen = [], set()
    for repo in repos:
        raw = sh(["git", "-C", repo, "worktree", "list", "--porcelain"], timeout=20) or ""
        paths = [l[len("worktree "):] for l in raw.splitlines() if l.startswith("worktree ")]
        main = paths[0] if paths else None
        for wt in paths[1:]:
            if wt in seen or not os.path.isdir(wt) or protected(wt):
                continue
            try:
                if os.stat(wt).st_dev != dev:
                    continue
            except OSError:
                continue
            seen.add(wt)
            out.append(entry(wt, "Worktree " + "/".join(wt.split("/")[-2:]), "worktree",
                             "Removes this checkout; its branch stays. git refuses if it has uncommitted or untracked changes.",
                             "git -C %s worktree remove %s" % (q(main), q(wt)), project=wt))
    return out


def covered(p, claimed):
    return any(p == c or c.startswith(p + "/") or p.startswith(c + "/") for c in claimed)


def unknown_items(claimed, dev):
    """Big folders nothing else claims: top-level ~/.dirs and children of the sweep roots."""
    roots = [r for r, _, _ in SWEEP_ROOTS]
    cands = []
    for e in os.scandir(HOME):
        if e.name.startswith(".") and e.name not in PRUNE_TOP and e.name not in VCS_DIRS and local_dir(e, dev) \
                and not covered(e.path, claimed + roots):
            cands.append((e.path,) + DOTDIR_NOTE)
    for root, consequence, manual in SWEEP_ROOTS:
        if not os.path.isdir(root):
            continue
        for e in os.scandir(root):
            if e.name.startswith("com.apple.") or e.name in SWEEP_SKIP or not local_dir(e, dev) or covered(e.path, claimed):
                continue
            cands.append((e.path, consequence, manual))
    return [entry(p, os.path.basename(p), "unknown", c, manual=m) for p, c, m in cands]


DOCKER_UNITS = {"B": 1, "KB": 1e3, "MB": 1e6, "GB": 1e9, "TB": 1e12}
DOCKER_SPEC = [  # (type, field to size by, label, prune subcommand, consequence)
    ("Build Cache", "Size", "build cache", "builder prune -af", "The next `docker build` re-runs every step. Images and containers aren't affected."),
    ("Images", "Reclaimable", "unused images", "image prune -af", "Removes every image no container uses; they're pulled or rebuilt when next needed."),
    ("Containers", "Reclaimable", "stopped containers", "container prune -f", "Deletes stopped containers and anything written inside them."),
    ("Local Volumes", "Reclaimable", "unused volumes", "volume prune -f",
     "Removes anonymous volumes no container uses; these can hold database data. Named volumes stay, so it may free less than shown."),
]


def docker_kib(s):
    m = re.match(r"([\d.]+)\s*([kKMGT]?B)", s or "")
    return int(float(m.group(1)) * DOCKER_UNITS[m.group(2).upper()] / 1024) if m else 0


def docker_items(skipped, notes):
    if not shutil.which("docker"):
        return []
    raw = sh(["docker", "context", "ls", "--format", "{{.Name}}\t{{.DockerEndpoint}}"])
    if raw is None:
        skipped.append("Docker (docker context ls failed)")
        return []
    out, seen = [], set()
    # "default" last, so an engine shared with a named context keeps the descriptive name.
    for line in sorted(raw.splitlines(), key=lambda l: l.startswith("default\t")):
        name, _, ep = line.partition("\t")
        name, ep = name.strip(), ep.strip()
        sock = ep[len("unix://"):] if ep.startswith("unix://") else None
        if sock and not os.path.exists(sock):
            if name != "default":
                skipped.append('Docker context "%s" (engine stopped, not measured)' % name)
            continue
        key = os.path.realpath(sock) if sock else ep  # Desktop's default and desktop-linux share one engine
        if key in seen:
            continue
        seen.add(key)
        df = sh(["docker", "--context", name, "system", "df", "--format", "{{json .}}"], timeout=30)
        if df is None:
            skipped.append('Docker context "%s" (engine not answering, not measured)' % name)
            continue
        rows = {}
        for l in df.splitlines():
            try:
                r = json.loads(l)
            except ValueError:
                continue
            rows[r.get("Type")] = r
        used = sum(docker_kib(r.get("Size")) for r in rows.values())
        free = sum(docker_kib(rows.get(t, {}).get(f)) for t, f, _, _, _ in DOCKER_SPEC)
        notes.append('Docker context "%s": %.1f GB in use, %.1f GB reclaimable by prune' % (name, used * 1024 / 1e9, free * 1024 / 1e9))
        for typ, field, label, sub, consequence in DOCKER_SPEC:
            kib = docker_kib(rows.get(typ, {}).get(field))
            if kib:
                it = entry(None, "Docker %s (%s)" % (label, name), "docker", consequence,
                           "docker --context %s %s" % (q(name), sub))
                it.update(id="docker:%s:%s" % (name, typ), display="docker (%s) · %s" % (name, typ.lower()), kib=kib)
                out.append(it)
    return out


def newest_mtime(root, depth=3):
    skip = set(ARTIFACTS) | VCS_DIRS
    best, stack = 0.0, [(root, 0)]
    while stack:
        d, lvl = stack.pop()
        try:
            for e in os.scandir(d):
                if e.is_symlink():
                    continue
                if e.is_dir():
                    if lvl < depth and e.name not in skip:
                        stack.append((e.path, lvl + 1))
                else:
                    best = max(best, e.stat().st_mtime)
        except OSError:
            pass
    return dt.date.fromtimestamp(best).isoformat() if best else None


def measure(items, skipped):
    with ThreadPoolExecutor(8) as ex:
        for it, (kib, why) in zip(items, ex.map(lambda i: du_kib(i["path"]), items)):
            it["kib"] = kib
            if why:
                skipped.append("%s (%s)" % (it["display"], why))
    return items


def drop_nested(items):
    """Keep the outermost of nested items (a worktree, not the node_modules inside it)."""
    kept = []
    for it in sorted(items, key=lambda i: len(i["path"] or "")):
        p = it["path"]
        if p and any(k["path"] and p.startswith(k["path"] + "/") for k in kept):
            continue
        kept.append(it)
    return kept


def read_history(path):
    prev = {}
    if os.path.exists(path):
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                if r.get("id") and r.get("kib"):
                    prev[r["id"]] = r  # last row per id wins
    last_at = max((r["scanned_at"] for r in prev.values()), default=None)
    return prev, last_at


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-mb", type=int, default=50)
    ap.add_argument("--out", default="~/disk-report")
    args = ap.parse_args()
    out_dir = os.path.expanduser(args.out)
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "sizes.csv")

    prev, last_at = read_history(csv_path)  # read first: growth needs the old state

    dev = os.stat(HOME).st_dev
    skipped = []
    found = [i for i in catalog() + runtime_items()
             if os.path.isdir(i["path"]) and not os.path.islink(i["path"])]
    artifacts, repos = walk_home(dev, skipped)
    found += artifacts + worktree_items(repos, dev)
    found += unknown_items([i["path"] for i in found], dev)
    measure(found, skipped)
    found = [i for i in found if i["kib"] is not None
             and (i["kind"] != "unknown" or i["kib"] >= UNKNOWN_MIN_KIB)]
    notes = []
    items = drop_nested(found) + docker_items(skipped, notes)
    items = [i for i in items if i["kib"] >= args.min_mb * 1024]

    now = dt.datetime.now().replace(microsecond=0)
    touched = {}
    for i in items:
        p = prev.get(i["id"])
        i["prevKib"] = int(p["kib"]) if p else None
        if not prev:
            i["status"] = "first"
        elif not p:
            i["status"] = "new"
        else:
            d = i["kib"] - i["prevKib"]
            big = abs(d) >= GROW_KIB and abs(d) >= GROW_PCT * max(i["prevKib"], 1)
            i["status"] = ("grew" if d > 0 else "shrank") if big else "same"
        proj = i.pop("project", None)
        if proj:
            if proj not in touched:
                touched[proj] = newest_mtime(proj)
            i["touched"] = touched[proj]
        i.pop("path", None)
    items.sort(key=lambda i: -i["kib"])

    new_file = not os.path.exists(csv_path)
    with open(csv_path, "a", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(CSV_COLUMNS)
        for i in items:
            w.writerow([now.isoformat(), i["id"], i["group"], i["kind"], i["kib"]])

    df = (sh(["df", "-k", "/System/Volumes/Data"]) or "").splitlines()
    total_k, _, free_k = (int(x) for x in df[1].split()[1:4]) if len(df) > 1 else (0, 0, 0)
    data = {"scannedAt": now.isoformat(), "lastScanAt": last_at, "diskTotalKib": total_k, "diskFreeKib": free_k,
            "minMb": args.min_mb, "protected": PROTECTED_NOTE, "skipped": skipped, "notes": notes, "items": items}
    with open(TEMPLATE) as f:
        html = f.read().replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
    report = os.path.join(out_dir, "report.html")
    with open(report, "w") as f:
        f.write(html)

    gb = lambda k: "%.1f GB" % (k * 1024 / 1e9)
    total = {g: sum(i["kib"] for i in items if i["group"] == g) for g in ("safe", "review")}
    print("report:", report)
    print("free: %s of %s" % (gb(free_k), gb(total_k)))
    print("safe to remove: %s   let me review first: %s   (%d items)" % (gb(total["safe"]), gb(total["review"]), len(items)))
    print("compared with:", last_at or "nothing (first run)")
    for i in sorted((i for i in items if i["status"] == "grew"), key=lambda i: i["prevKib"] - i["kib"]):
        print("GREW  %s  %s -> %s" % (i["display"], gb(i["prevKib"]), gb(i["kib"])))
    for n in notes:
        print("NOTE", n)
    for s in skipped:
        print("SKIPPED", s)


if __name__ == "__main__":
    sys.exit(main())
