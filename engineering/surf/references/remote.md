# Remote Surf

Read this when controlling a browser on another machine.

Remote clients require a per-client credential; Tailnet reachability alone is not authorization. On the POSIX browser host, authorize the client before installing the listener:

```bash
surf remote authorize agent-macbook --output ~/agent-macbook.surf-credential.json
surf install <extension-id> --listen 100.101.102.103:4321
surf remote list
```

Move the mode-0600 credential to the client through a secure channel. It grants full trusted Surf authority. Use it explicitly or through `SURF_REMOTE` and `SURF_REMOTE_CREDENTIAL`:

```bash
surf --remote 100.101.102.103:4321 \
  --remote-credential ~/.config/surf/agent-macbook.json \
  page.read

surf remote revoke agent-macbook  # Run on the browser host
```

## Remote paths and transfer limits

Remote paths are client-local by default. `local:./file` is explicit client-local syntax; only `remote:/absolute/path` accesses the browser host directly. Remote transfer supports one upload or ChatGPT/Gemini input and one screenshot, network-export, or Gemini image output. Limits are 256 MiB per file, 512 MiB and 32 files per connection, and 256 KiB decoded chunks. `record`, `aistudio.build`, smoke screenshot directories, directories, and multi-file inputs are not supported remotely. Successful action screenshots and failure `--auto-capture` diagnostics are transferred back to client-local paths.
