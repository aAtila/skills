# Surf Advanced — Emulation, Network, Workflows, Playbooks

Read this for device/network emulation, network capture and HAR export, console/perf tracing, cookies, history, smoke tests, named workflows, playbooks, or the socket API.

## Device/Network Emulation

```bash
# Network throttling
surf emulate.network slow-3g   # Presets: slow-3g, fast-3g, 4g, offline
surf emulate.network reset     # Disable throttling

# CPU throttling
surf emulate.cpu 4             # 4x slower
surf emulate.cpu 1             # Reset

# Device emulation (19 presets)
surf emulate.device "iPhone 14"
surf emulate.device "Pixel 7"
surf emulate.device --list     # List available devices

# Custom viewport
surf emulate.viewport --width 1280 --height 720
surf emulate.touch --enable    # Enable touch emulation

# Geolocation
surf emulate.geo --lat 37.7749 --lon -122.4194
surf emulate.geo --clear
```

## Network Inspection

```bash
surf network                   # List captured requests
surf network --stream          # Real-time network events
surf network.get --id "req-123"   # Full request details
surf network.body --id "req-123"  # Get response body
surf network.curl --id "req-123"  # Generate curl command
surf network.origins           # List origins with stats
surf network.stats             # Capture statistics
surf network -vv --body-mode text --per-body-bytes 65536
surf network.export --har --output ./trace.har
surf network.clear             # Clear captured requests
```

Response-body capture supports `none`, `text`, and `all` modes plus per-body and per-tab-session byte caps. HAR exports carry body completeness metadata. Persistent network state is private under `~/.surf/state/network/` by default; configure `SURF_NETWORK_PATH` in the native host environment to change it.

## Console

```bash
surf console                   # Get console messages
surf console --stream          # Real-time console
surf console --stream --level error  # Errors only
```

## Performance

```bash
surf perf.metrics              # Current metrics snapshot
surf perf.start                # Start trace
surf perf.stop                 # Stop and get results
```

## Zoom

```bash
surf zoom                      # Get current zoom level
surf zoom 1.5                  # Set zoom to 150%
surf zoom 1                    # Reset to 100%
```

## Cookies & Storage

```bash
surf cookie list               # List cookies for current page
surf cookie list --domain .google.com
surf cookie set --name "token" --value "abc123"
surf cookie get "token"
surf cookie clear --all        # Clear all cookies
surf cookie delete "token"     # Clear one cookie
```

## History & Bookmarks

```bash
surf history --query "github" --max 20
surf bookmarks --query "docs"
surf bookmark.add --url "https://..." --title "My Bookmark"
surf bookmark.remove
```

## Health Checks & Smoke Tests

```bash
surf health --url "http://localhost:3000"
surf smoke --urls "http://localhost:3000" "http://localhost:3000/about"
surf smoke --urls "..." --screenshot /tmp/smoke
```

## Named Workflows

Save workflows as JSON files in `~/.surf/workflows/` (user) or `./.surf/workflows/` (project):

```bash
# List available workflows
surf workflow.list

# Show workflow details
surf workflow.info my-workflow

# Run by name with arguments
surf do my-workflow --email "user@example.com" --password "secret"

# Validate workflow file
surf workflow.validate workflow.json
```

### Workflow JSON Format

```json
{
  "name": "Login Flow",
  "description": "Automate login process",
  "args": {
    "email": { "required": true },
    "password": { "required": true },
    "url": { "default": "https://example.com/login" }
  },
  "steps": [
    { "tool": "navigate", "args": { "url": "%{url}" } },
    { "tool": "type", "args": { "text": "%{email}", "selector": "input[name=email]" } },
    { "tool": "type", "args": { "text": "%{password}", "selector": "input[name=password]" } },
    { "tool": "click", "args": { "selector": "button[type=submit]" } },
    { "tool": "screenshot", "args": {}, "as": "result" }
  ]
}
```

### Loops and Step Outputs

```json
{
  "steps": [
    // Capture step output for later use
    { "tool": "js", "args": { "code": "return [1,2,3]" }, "as": "items" },

    // Fixed iterations
    { "repeat": 5, "steps": [
      { "tool": "click", "args": { "ref": "e5" } }
    ]},

    // Iterate over array
    { "each": "%{items}", "as": "item", "steps": [
      { "tool": "js", "args": { "code": "console.log('%{item}')" } }
    ]},

    // Repeat until condition
    { "repeat": 20, "until": { "tool": "js", "args": { "code": "return done" } }, "steps": [...] }
  ]
}
```

### Workflow Options

```bash
--file, -f <path>     # Load from JSON file
--dry-run             # Parse and validate without executing
--on-error stop|continue  # Error handling (default: stop)
--step-delay <ms>     # Delay between steps (default: 100, 0 to disable)
--no-auto-wait        # Disable automatic waits
--json                # Structured JSON output
```

**Auto-waits:** Commands automatically wait for completion:
- Navigation (`go`, `back`, `forward`) → waits for page load
- Clicks, key presses, form fills → waits for DOM stability
- Tab switches → waits for tab to load

## Playbooks

Use `surf do` for a direct command sequence. Use a playbook for a reusable site capability with provenance, browser-session network execution, workflow fallback, and write-safety policy.

```bash
surf playbook list
surf pb show page
surf pb ops page
surf use page read --json
```

Resolution order is project (`./.surf/playbooks/`), user (`~/.surf/playbooks/`), then built-in. Provider compatibility commands stay on their validated command paths until provider playbooks have real login-flow validation. A write op requires `--write`; Surf records semantic intent before dispatch so a timeout or concurrent retry cannot silently double-submit.

Author from redacted recent activity when it contains only read/navigation behavior, or use an explicit record for richer evidence:

```bash
surf pb suggest --since 1h
surf pb save example --op read --from-recent 1h
surf pb record start example --op read --network --watch
surf pb record mark "loaded results"
surf pb record stop --draft
surf pb save --from-record <record-id>
surf pb trace export --from-record <record-id> --har ./trace.har
surf pb export example --out ./example-playbook
surf pb import ./example-playbook
```

Records, trace slices, receipts, and the bounded activity journal are private Surf state. Inputs and authentication headers are redacted by default. Use `--include-input-values` only when the saved values are necessary and acceptable.

Client projections replay a validated read endpoint and never embed captured browser credentials:

```bash
surf pb client derive example --op read --from-record <record-id> --request-id <request-id> --out ./client
surf pb client export example --op read --out ./client
surf pb client verify ./client
```

## Socket API

For programmatic access:

```bash
echo '{"type":"tool_request","method":"execute_tool","params":{"tool":"tab.list","args":{}},"id":"1"}' | nc -U /tmp/surf.sock
```
