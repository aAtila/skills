"""Read-only scanner regressions with mocked disk/service output.

Run: python3 -m unittest discover -s evals -p 'test_*.py'
No real cache is scanned or deleted; scan() receives a temporary fixture root.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCANNER = Path(__file__).resolve().parents[1] / "scripts" / "scan.sh"


class ScanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "fixture home"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for relative in (
            "Library/Caches/Homebrew", "Library/Caches/Google",
            "Library/Developer/CoreSimulator/Devices", ".Trash",
            "Library/Application Support/RepoPrompt CE/Conductor/BuildCache",
            ".claude/telemetry", "CODE/project with spaces/.build",
            "CODE/project with spaces/node_modules",
        ):
            directory = self.home / relative
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "keep.txt").write_text("sentinel\n")
        self.mock("df", "print('Filesystem 1024-blocks Used Available Capacity Mounted on')\nprint('fixture 100000 40000 60000 40% /')")
        self.mock("diskutil", """
if os.environ.get('SCAN_TEST_SERVICES') == 'failed':
    sys.exit(1)
print('Container Total Space: 100 GB (100000000000 Bytes)')
print('Container Free Space: 40 GB (40000000000 Bytes)')
""")
        self.mock("tmutil", """
if os.environ.get('SCAN_TEST_SERVICES') == 'failed':
    sys.exit(1)
print('Snapshots for disk /:')
""")
        self.mock("du", """
p = sys.argv[-1]
if os.environ.get('SCAN_TEST_DU') == 'partial' and p.endswith('/.Trash'):
    print('1024\\t' + p)
    sys.exit(1)
if '-kxd' in sys.argv:
    print('1048576\\t' + p + '/child')
    print('2097152\\t' + p)
else:
    print('1048576\\t' + p)
""")
        self.env = dict(os.environ)
        self.env["PATH"] = str(self.bin) + os.pathsep + self.env["PATH"]
        # Keep the real HOME unchanged; pass a fixture root to scan().
        for name in ("ANDROID_HOME", "ANDROID_SDK_ROOT", "ANDROID_AVD_HOME", "ANDROID_USER_HOME"):
            self.env.pop(name, None)

    def mock(self, name, body):
        script = self.bin / name
        script.write_text(f"#!{sys.executable}\nimport os, sys\n" + body + "\n")
        script.chmod(0o755)

    def run_scan(self, deep=0):
        before = {str(p): p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
        result = subprocess.run(
            ["/bin/bash", "-c", 'source "$1"; scan "$2" "$3"',
             "scan-test", str(SCANNER), str(self.home), str(deep)],
            env=self.env, text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        after = {str(p): p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
        self.assertEqual(before, after, "read-only scan modified fixture data")
        return result.stdout, result.stderr

    def test_failed_service_queries_are_unknown(self):
        self.env["SCAN_TEST_SERVICES"] = "failed"
        out, _ = self.run_scan()
        self.assertIn("snapshots: unknown", out)
        self.assertNotIn("snapshots: 0", out)
        self.assertIn("Unavailable: container totals", out)

    def test_candidate_scope_excludes_parent_totals(self):
        out, _ = self.run_scan()
        candidates = [line for line in out.splitlines() if " [" in line]
        paths = {line.split("] ", 1)[1] for line in candidates}
        self.assertNotIn(str(self.home / "Library/Caches"), paths)
        self.assertIn(str(self.home / "Library/Caches/Homebrew"), paths)
        self.assertIn(str(self.home / "Library/Caches/Google"), paths)
        self.assertTrue(any("[CHECK]" in line and line.endswith("/.Trash") for line in candidates))
        self.assertTrue(any("[CHECK]" in line and line.endswith("CoreSimulator/Devices") for line in candidates))
        self.assertTrue(any(line.endswith("Conductor/BuildCache") for line in candidates))
        self.assertIn("snapshots: 0", out)

    def test_partial_measurement_is_not_ranked_as_complete(self):
        self.env["SCAN_TEST_DU"] = "partial"
        out, err = self.run_scan()
        self.assertIn("Unknown/partial size", err)
        self.assertFalse(any("[CHECK]" in line and line.endswith("/.Trash") for line in out.splitlines()))

    def test_deep_scan_preserves_spaced_project_paths(self):
        out, _ = self.run_scan(deep=1)
        deep = out.split("## DEEP", 1)[1].split("## ACCOUNTING", 1)[0]
        self.assertIn(str(self.home / "CODE/project with spaces/.build"), deep)
        self.assertIn(str(self.home / "CODE/project with spaces/node_modules"), deep)
        self.assertNotIn("keep.txt", deep)


if __name__ == "__main__":
    unittest.main()
