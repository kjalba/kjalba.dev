---
title: "Scaffolding kjalba.dev"
date: 2025-07-15
description: "How I built and architected this site — Hugo, Blowfish, Cloudflare Pages, and an agent-agnostic Dev Log system."
tags: ["hugo", "blowfish", "cloudflare", "architecture", "ai-agents"]
projects:
  - name: "kjalba.dev"
    url: "https://github.com/kjalba/kjalba.dev"
draft: false
---

Finally got the personal site off the ground. This one's been on the to-do list for a while.

## The stack

**Hugo** for static generation — it's fast, Markdown-native, and the ecosystem is mature. I picked the **Blowfish** theme because it's built on Tailwind CSS and has exactly the profile card + card list aesthetic I wanted. It's the theme behind merox.dev, which was one of the main inspirations here. Dark mode by default, slate colour scheme.

Deployed on **Cloudflare Pages** — free tier, auto-deploys on every push to `main`, global CDN. No build scripts to maintain, no dashboard to babysit.

## The interesting part: the Dev Log

The part I spent the most time thinking through was this section you're reading right now.

The easy answer would have been: Bob (my AI agent in the dev-web workspace) writes posts here when I ask it to. Simple, but vendor-locked and brittle — what about the sessions I'm doing in Cursor, or Claude Code, or Windsurf?

The architecture I landed on has two layers:

**Layer 1 — Capture.** A file at `~/dev-journal/DEVLOG_FEED.md` that lives outside any specific project. Every project repo gets an `AGENTS.md` — an open standard now backed by the Linux Foundation, supported by Claude Code, Cursor, Windsurf, Copilot, Gemini CLI, and most other major tools. That file instructs whatever agent is running to append a structured entry to the feed at the end of each session: what was worked on, decisions made, tradeoffs, interesting discoveries.

**Layer 2 — Publish.** When I want a Dev Log post, I ask any agent to read the feed file and synthesise recent entries into a post. The agent knows the Hugo front matter schema from `AGENTS.md` in this repo. Push, deploy, done.

The key thing: no single agent is required. Whatever tool I'm using that day can both capture and publish. The feed file is the stable contract between all of them.

## What I decided and why

- **Profile layout over hero** — launch with content-forward. A big banner image when there's nothing behind it yet would feel hollow.
- **No CMS** — everything is Markdown files in git. Adding a blog post, project, or YouTube video is just creating a `.md` file. This site should be zero-friction to maintain.
- **No comments system** — for now. Can add Giscus (GitHub Discussions-based) later if there's an audience worth talking to.

## What's next

- Add a profile photo
- Fill in the real work history on the About page
- Push to GitHub and wire up Cloudflare Pages
- Write the first real technical blog post
