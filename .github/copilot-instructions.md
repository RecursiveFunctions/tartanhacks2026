# Copilot instructions for tartanhacks2026

These instructions help an AI coding agent become productive quickly in this repository.

Summary
- **Project purpose**: convert Instagram DMs and offline availability data into meetup coordination and DM automation (see `README.md` mermaid diagram).
- **Main components (intended)**: `Uvicorn` service (port 8000) running an MCP-like server, `instagrapi` for Instagram integration, a local LLM (Ollama) for decision logic, and a Cloudflared tunnel to expose a public URL (`friend-roulette.cm-unity.org`).

Quick facts you can rely on
- **Single-entry script present**: `friend-roulette-overlaps.py` — demonstrates CSV parsing and availability overlap logic. Use it as a small, concrete example of coding/style in this repo.
- **Primary CSV**: `CMU Friend Roulette Availability Responses - Form Responses 1.csv` — scripts expect it to be in the repo root when run.
- **Empty module stub**: `instagram_dm_mcp/` exists but is empty; do not assume implemented MCP service code is present.

How to be helpful (actionable rules)
- **Do not invent missing services**: README documents intended architecture (Uvicorn, Instagrapi, Cloudflared, Ollama). If code for these components is missing, create small, well-scoped PRs, tests, or TODO issues rather than scaffolding large subsystems without confirmation.
- **Follow local examples**: Mirror patterns from `friend-roulette-overlaps.py` when manipulating CSVs and scheduling logic: it uses `csv.DictReader`, column-name patterns like `Please check which hour blocks`, and `itertools.combinations` for pairwise comparisons.
- **Be explicit about runtime commands**: recommend running the CSV script locally as:

```
python3 friend-roulette-overlaps.py
```

  Confirm the CSV file is present in the working directory before running.
- **Configuration & dependencies**: there is no `requirements.txt` or environment file in the repo. If you add dependencies, include `requirements.txt` and usage notes. When suggesting commands, show exact shell commands for macOS `zsh`.

Code and style specifics
- **Small, single-file scripts**: keep changes minimal and focused — this repo favors readable scripts over heavy frameworks.
- **Time parsing conventions**: the project converts strings like `7am` / `3pm` to minutes via helper functions (see `hour_to_minutes`, `minutes_to_hour`). Reuse or extend these helpers rather than adding alternative time libraries for small features.
- **Availability column parsing**: the script strips trailing `s` from days (e.g., `Mondays` -> `Monday`) and expects hour-block labels of form `X - Y` where `X` and `Y` are hour strings.

Integration and testing guidance
- **Local testing**: run the available script directly to validate logic. Add small unit tests around `parse_availability`, `hour_to_minutes`, and `condense_hour_blocks` when extending scheduling logic.
- **When proposing MCP/Instagrapi work**: reference the README mermaid flow and create incremental PRs: (1) add API surface stubs, (2) add config (env vars) and a `README` section explaining how to run `cloudflared` and `uvicorn`, (3) add integration tests or mocks for `instagrapi` calls.

Files worth inspecting when working on features
- `README.md` — architecture and expected runtime topology.
- `friend-roulette-overlaps.py` — canonical example of parsing logic and output formatting.
- `CMU Friend Roulette Availability Responses - Form Responses 1.csv` — source data used by the script.
- `instagram_dm_mcp/` — placeholder for MCP-related code; treat as design target, not implemented code.

PR guidance
- Keep PRs small and self-contained. Add `requirements.txt` when introducing dependencies. Include an example command to reproduce the change locally (shell commands for `zsh`).
- If you change parsing behavior for the CSV, include a short note describing real-world CSV quirks you accounted for (empty cells, extra whitespace, alternate day forms).

If anything is unclear
- Ask the maintainer for the intended Python version and any missing dependency lists before scaffolding networked services.
- If you need to add MCP or Instagrapi integration, create an RFC-style issue/PR first linking to `README.md` diagram and list minimal acceptance criteria.

End of instructions — request feedback if you want this tuned for testing, linting, or CI steps.
