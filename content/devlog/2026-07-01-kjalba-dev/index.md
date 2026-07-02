---
title: "kjalba.dev: AI dev log"
date: 2026-07-01
description: "Scaffolded the personal portfolio site using Hugo and the Blowfish theme. Set up the full config directory structure, all section pages (blog, projects, devlog, youtube, about), and the agent-agnostic Dev Log architecture. The site builds and deploys via Cloudflare Pages."
tags: ["kjalba-dev", "bob", "chess-trainer-cli", "claude-code"]
sourceEntryIds:
  - "4e2a1564de27e274ccf7c71918cbaa1f69a6cc252145ccac58bc6af58b853c3b"
  - "f75ce46ac970dda8496c4346ff606608a134293bee9eedd516528727927d8d39"
projects:
  - name: "kjalba.dev"
    url: "https://github.com/kjalba/kjalba.dev"
  - name: "chess-trainer-cli"
    url: "https://github.com/kjalba/chess-trainer-cli"
draft: false
---

*This entry was drafted from the shared devlog feed by an AI agent and should be reviewed before publishing.*
## 2026-06-24 — kjalba.dev
**Agent:** bob  **Session length:** long
Scaffolded the personal portfolio site using Hugo and the Blowfish theme. Set up the full config directory structure, all section pages (blog, projects, devlog, youtube, about), and the agent-agnostic Dev Log architecture. The site builds and deploys via Cloudflare Pages.
### Decisions made
- Chose Hugo + Blowfish over Astro because Blowfish directly matches the merox.dev aesthetic we were inspired by, and Hugo build speed is exceptional
- Chose Cloudflare Pages over GitHub Pages for better CDN and free analytics
- Chose slate colour scheme (dark mode default) for clean technical aesthetic
- Chose shared ~/dev-journal/DEVLOG_FEED.md over single-agent approach so any tool (Cursor, Claude Code, Windsurf, etc.) can contribute -- agent-agnostic via AGENTS.md standard
- Chose profile homepage layout over hero because content-forward is right at launch
### Interesting discoveries
- Blowfish v2 uses Hugo Modules (not themes/ git submodule) -- much cleaner to update
- Hugo has a built-in youtube shortcode so no third-party dependency needed for the YouTube section
- AGENTS.md is now an open Linux Foundation standard supported across Claude Code, Cursor, Windsurf, Copilot, Gemini CLI
- YouTube thumbnail URL pattern https://img.youtube.com/vi/{ID}/maxresdefault.jpg works without any API key
### What's next
- Add profile photo to assets/img/avatar.jpg
- Fill in real work history in about/index.md
- Push to GitHub and connect Cloudflare Pages
- Add first real blog post

## 2026-07-01 — chess-trainer-cli
**Agent:** claude-code  **Session length:** medium
Added random puzzle support and an interactive launch menu to the chess trainer CLI.
Users can now choose between daily and random puzzles from a menu, or skip it with flags.
Random puzzles support 70+ Lichess theme filters and 5 difficulty levels, authenticated via the Lichess API.
### Decisions made
- Chose flags (`--theme`, `--difficulty`) over menu selection for themes because there are 70+ options - too many for an interactive list, and flags compose naturally with the `-rp` shortcut
- Chose environment variable (`LICHESS_API_TOKEN`) over config file or flag for the API token - simplest approach for a CLI tool, no config plumbing needed
- Switched from `/api/puzzle/next` to `/api/puzzle/batch/{angle}` endpoint because `/next` returns the same puzzle until you POST a completion result back. The batch endpoint lets us fetch 50 puzzles and pick one at random, giving immediate variety
- POST puzzle completion back to Lichess as best-effort - if the token lacks `puzzle:write` scope it silently fails, but the random pick from the batch still provides variety
- Extracted shared PGN-parse-draw-play logic into a `startPuzzle` helper to avoid duplicating the game flow between daily and random handlers
### Interesting discoveries
- The Lichess `/api/puzzle/next` endpoint is session-stateful - it tracks which puzzle you're "on" and won't advance until you round-trip a completion. This isn't obvious from the docs, which just say "get a new puzzle"
- The Lichess API docs page is fully JS-rendered and can't be scraped, but the raw OpenAPI spec is available on GitHub at `lichess-org/api` with per-endpoint YAML files under `doc/specs/tags/`
- The batch endpoint's POST uses a different schema (`PuzzleBatchSolveRequest`) than what you might guess - it takes a `solutions` array with `id`, `win`, and `rated` fields
### What's next
- Track win/loss accurately in `HandleUserInput` (return whether user solved without skipping) and pass that to the completion POST
- Consider caching the batch locally so multiple runs don't re-fetch the same 50 puzzles
- The `rated` field in the completion POST could let users opt into Lichess rating updates from the CLI

