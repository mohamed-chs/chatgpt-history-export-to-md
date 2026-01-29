# Development Workflow & Agent Protocol

## Release Workflow
To publish a new version to PyPI (automated via GitHub Actions):

```bash
# 1. Bump version (patch/minor/major)
# This updates pyproject.toml and uv.lock
uv version --bump patch

# 2. Commit changes
git add pyproject.toml uv.lock
git commit -m "chore: bump version to X.Y.Z"

# 3. Create and push tag
# This triggers the 'Release' workflow which builds and publishes to PyPI
git tag vX.Y.Z
git push && git push origin vX.Y.Z
```

## Agent Protocol
- **Startup**: **CRITICAL: YOU MUST ALWAYS START** by reading [`docs/dev/HANDOFF.md`](docs/dev/HANDOFF.md), then conduct a **DEEP CODEBASE ANALYSIS** to understand the current state, conventions, and architectural patterns. This is **MANDATORY FOR EVERY SESSION.**
- **Critical Mindset**: **DO NOT ASSUME** the codebase is perfectly implemented. Be alert for missing or buggy logic, including features that may appear complete but still require refinement or further work.
- **Verification**: **ALWAYS** run the full quality gate before submitting changes (or at minimum `uv run ruff check` for docs-only work).
- **Docs stay current**: **REFLEXIVELY** keep relevant `.md` docs updated when behavior/UX changes (README, `docs/dev/HANDOFF.md`, and any feature docs touched by the change).
- **Persistence**: If you leave incomplete work, update `docs/dev/HANDOFF.md` (do not store tasks here).
- **Commits**: Prefer small, logically-scoped commits with tests for behavioral changes.

## Communication & UX Protocol
- **Directness**: If you need the user to run a test, inspect a file, or provide context, **ASK** directly. Do not implement complex workarounds to avoid user interaction.
- **Push back when helpful**: The maintainer is almost always open to you questioning prompts, proposing refinements/better ideas, or even rejecting an idea if you think it’s harmful/incorrect (hey, it's me; I'm not a very experienced programmer).
- **User Experience**: Prioritize the end-user experience (UX) of the application. Do not compromise the application's design or usability to fit temporary development environment constraints.
- **Transparency**: Be transparent about missing context or difficulties.
