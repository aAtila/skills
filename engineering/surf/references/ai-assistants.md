# AI Assistants via Surf (No API Keys)

Query AI models using your browser's logged-in session. Must be logged into the respective service in Chrome (chatgpt.com, gemini.google.com, perplexity.ai, x.com, or aistudio.google.com).

## ChatGPT
```bash
surf chatgpt "explain this code"
surf chatgpt "summarize" --with-page              # Include current page context
surf chatgpt "review" --model gpt-5.5             # Specify model
surf chatgpt "analyze" --file document.pdf        # With file attachment
```

## Oracle

Use `surf chatgpt` for quick one-shot questions. Use `surf oracle` for long-running or Pro coding consults that need a durable job, explicit model and effort selection, file context, recovery, or follow-up turns. Oracle is local-only.

For agent workflows, detach after dispatch and keep the returned `.id`:

```bash
surf oracle ask "Review this change and identify release risks" \
  --files "src/**/*.ts" --files "package.json" \
  --model gpt-5.5 --effort pro --detach --json

surf oracle status <job-id> --json
surf oracle result <job-id> --json
# Or let Surf keep polling until capture:
surf oracle result <job-id> --wait --json
```

`status` reads persisted state without touching Chrome. `result` attempts to harvest the answer and returns the job object with `response` once its state is `captured`. A Ctrl-C during waiting exits with status 130 and prints `Recover with: surf oracle result <id>`. Once the job is `awaiting`, the persisted ChatGPT conversation URL is its durable key, so `surf oracle result <id>` can recover after CLI exit, native-host restart, or Chrome restart by reopening that conversation.

Treat Pro quota as scarce. Oracle never selects Pro implicitly; request it with `--model pro` or `--effort pro`. ChatGPT model aliases include `instant`, `thinking`, `pro`, `gpt-5.5`, and `gpt-5.6-sol`. Accepted `--effort` values are `light`, `standard`, `extended`, `heavy`, and `pro`. Requested model and effort selections are read back before submission, and an unverifiable selection fails with `model_verification_failed` instead of silently continuing. Capacity is one non-terminal oracle job. A `capacity` error includes the in-flight job ID; poll that job or wait for it to finish rather than submitting the same consult again.

When loaded as a Pi extension, Surf also registers a `surf-oracle` external-job provider when the runtime exposes that bridge. The provider maps `start`, `status`, `result`, and `reattach` to durable Surf Oracle jobs and returns pi-subagents' external-job contract shape: `providerJobId`, a contract state (`queued`, `running`, `completed`, `failed`), the conversation URL, the captured result text as `output`, and failure code and message. It honors `options.model` and `options.effort` for starts, so `model: pro` selects ChatGPT GPT-5.6 Sol Pro web mode through the browser. `reattach` only harvests an existing job by ID; it never submits the prompt again.

When Surf is installed as a Pi package, it exposes an optional `gpt-pro` package agent for `pi-subagents`. That profile uses `runner.type: external-job`, provider `surf-oracle`, and `options.model: pro`. Surf remains useful without Pi or `pi-subagents`.

Context comes from repeatable `--files` globs. Surf fails closed when a glob matches nothing or a matched file is unreadable, binary, or invalid UTF-8. It also blocks gitignored files and basenames matching `.env*`, `*.pem`, `*.key`, `id_rsa*`, `id_ed25519*`, `*.p12`, `*.pfx`, `credentials*`, or `secrets*`. Use `--allow-sensitive` only after intentionally reviewing those files; it overrides the block rather than redacting content. Context up to 60,000 evidence characters is inserted inline, while larger context becomes one private text attachment. The assembly manifest records each path, byte count, SHA-256, inline or bundle disposition, and deny-list outcome.

Continue a captured consult with `follow`. Use the ID returned by each turn for the next turn:

```bash
surf oracle follow <job-id> "Challenge your recommendation. What could invalidate it?" --detach --json
surf oracle result <follow-job-id> --wait --json
surf oracle follow <follow-job-id> "Give the final decision and concrete next steps." --detach --json
```

## Gemini
```bash
surf gemini "explain quantum computing"
surf gemini "summarize" --with-page               # Include page context
surf gemini "analyze" --file data.csv             # Attach file
surf gemini "a robot surfing" --generate-image /tmp/robot.png
surf gemini "add sunglasses" --edit-image photo.jpg --output out.jpg
surf gemini "summarize" --youtube "https://youtube.com/..."
surf gemini "hello" --model gemini-3.5-flash      # Models: gemini-3.1-pro (default), gemini-3.5-flash, gemini-3.1-flash-lite
surf gemini "wide banner" --generate-image /tmp/banner.png --aspect-ratio 16:9
```

## Perplexity
```bash
surf perplexity "what is quantum computing"
surf perplexity "explain this page" --with-page   # Include page context
surf perplexity "deep dive" --mode research       # Research mode (Pro)
surf perplexity "latest news" --model sonar       # Model selection (Pro)
```

## Grok (via x.com - requires X.com login in Chrome)
```bash
surf grok "what are the latest AI trends on X"    # Search X posts
surf grok "analyze @username recent activity"     # Profile analysis
surf grok "summarize this page" --with-page       # Include page context
surf grok "find viral AI posts" --deep-search     # DeepSearch mode
surf grok "quick question" --model fast           # Models: auto, fast, expert, grok-4.20-beta
```

For exhaustive, multi-angle X research with categorized findings and full post-URL traceability, use the `deep-x-research` skill (`skills/deep-x-research/`) instead of a single Grok query.

**Grok Validation & Troubleshooting:**
```bash
# Validate Grok UI and check available models (no query sent)
surf grok --validate

# If models changed, save discovered models to surf.json config
surf grok --validate --save-models
```

## AI Studio (via aistudio.google.com - requires Google login in Chrome)
```bash
surf aistudio "explain quantum computing"
surf aistudio "redteam this" --with-page          # Include current page context
surf aistudio "quick answer" --model gemini-3-flash-preview  # Model selection
surf aistudio "analyze" --timeout 600             # Custom timeout (default: 300s)
```

**Why AI Studio over Gemini?** AI Studio gives access to less restricted Gemini models. For Gemini 3 Pro the difference can be significant with certain prompts. Downside: aggressive per-day rate limits on Pro and Flash models.

**Model selection is best-effort:** Pass any AI Studio model id (e.g. `gemini-3.1-pro-preview`, `gemini-3-flash-preview`, `gemini-flash-lite-latest`). If the model isn't found, AI Studio uses whatever model was last selected in the UI.

## AI Studio App Builder
```bash
surf aistudio.build "build a portfolio site"
surf aistudio.build "todo app" --model gemini-3.1-pro-preview   # Model override
surf aistudio.build "crm dashboard" --output ./out              # Extract zip to directory
surf aistudio.build "game" --keep-open --timeout 600            # Keep tab open, 10min timeout
```

Automates AI Studio's App Builder at `aistudio.google.com/apps`. Types your prompt, clicks Build, waits for completion, downloads the generated zip, and optionally extracts it.

- `--output <dir>` extracts the zip to a directory
- `--model <id>` overrides the model in Advanced Settings
- `--timeout <seconds>` build timeout (default: 600s)
- `--keep-open` leaves the AI Studio tab open after completion

Returns `zipPath`, `extractedPath`, `model`, `buildDuration`, and `tookMs`.

## AI Tool Troubleshooting

When AI queries fail, check these common issues:

1. **Not logged in**: The error "login required" means you need to log into the service in Chrome (chatgpt.com, gemini.google.com, perplexity.ai, x.com, or aistudio.google.com)
2. **Model selection failed**: The UI may have changed. Run `surf grok --validate` to check
3. **Response timeout**: Reasoning-heavy models (ChatGPT o1, Grok Expert) can take 45+ seconds. AI Studio builds can take several minutes.
4. **Element not found**: The service's UI changed. Check for surf-cli updates

**Debugging workflow for agents:**
```bash
# 1. Check if the service is accessible and UI is valid
surf grok --validate

# 2. If models mismatch, update the local settings
surf grok --validate --save-models

# 3. Retry with explicit model name from validation output
surf grok "query" --model <model-from-validation>

# 4. If still failing, try with longer timeout
surf grok "query" --timeout 600
```

## Tips

- AI tools use the browser session — must be logged into the service, no API keys needed.
- Run `surf grok --validate` if queries fail, to check for UI changes.
- Use long timeouts for reasoning-heavy models — ChatGPT o1 and Grok Expert can take 60+ seconds; AI Studio builds default to 600s.
- `surf aistudio` gives less filtered responses than `surf gemini` for the same models.
- Provider commands (`chatgpt`, `gemini`, `perplexity`, `grok`, `kimi`, `aistudio`, `oracle ask`) take exclusive browser access and print a warning before dispatch. Do not assume Surf is hung while that warning is visible; inspect `surf session.info <name>` from another shell to see the active writer.
