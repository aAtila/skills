# Surf Troubleshooting — Native Host / Socket

Read this when a surf command fails with `Socket connect failed`, native messaging errors, or after a fresh install.

## Diagnosis order

1. Run `surf doctor` (or `surf doctor --browser all`) before guessing at reinstall steps.
2. Check the `Attempted socket:` line in the output. Default sockets are `/tmp/surf.sock` on macOS/Linux/WSL2 and `//./pipe/surf` on Windows.
3. If `SURF_SOCKET` is set, the browser-launched host and the shell running `surf` must use the same value.

## macOS native messaging

Chrome reads the native messaging manifest at `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/surf.browser.host.json`. If native messaging fails:

1. Confirm that file exists and its `allowed_origins` extension ID matches `chrome://extensions`.
2. Rerun `surf install <extension-id>`.
3. Restart Chrome, reload the extension, and inspect the extension service-worker console.

## WSL2 with Windows Chrome

Run `surf install <extension-id>` inside WSL2. Surf detects WSL2 and writes the Windows-side native messaging manifest plus a wrapper that launches the WSL host. Use `surf install <extension-id> --target linux` only for Linux browsers running inside WSLg.
