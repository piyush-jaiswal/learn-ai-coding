---
description: Run the SlopLang playground in the background on an optional port (default 8080)
---

Start the SlopLang playground server in the background.

1. Use `$ARGUMENTS` as the port, or `8080` when no argument is given.
2. Run `lsof -nP -iTCP -sTCP:LISTEN` and inspect the listening processes.
3. Check for an existing sloperator playground server. If one is already running, do not start a second one: report its PID, port, and URL, then stop. If the `COMMAND` column is truncated, inspect the PID with `ps -p <PID> -o command=`.
4. If the requested port is already occupied by a different process, report the conflict and stop instead of starting the server.
5. Otherwise run `uv run playground/server.py <port>` as a background command, then verify the new listener and report the URL (`http://localhost:<port>`).
