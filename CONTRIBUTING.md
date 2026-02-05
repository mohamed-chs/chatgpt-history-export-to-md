# Contributing to Convoviz

Thanks for your interest in contributing! This guide covers the essentials.

---

## Reporting Bugs

Before reporting, search existing issues and update to the latest version.

Include:
- **Convoviz version**: `convoviz --version`
- **Python version**: `python --version`  
- **OS**: Windows, macOS, or Linux
- **Steps to reproduce**
- **Error messages** (full traceback if available)

👉 **[Open a Bug Report](https://github.com/mohamed-chs/convoviz/issues/new?template=bug_report.md)**

---

## Suggesting Features

Check existing issues first. Describe the problem you're solving and your proposed solution.

👉 **[Open a Feature Request](https://github.com/mohamed-chs/convoviz/issues/new?template=feature_request.md)**

---

## Looking for Ideas?

Contributions are particularly welcome in the following areas:

### 📊 Enriching Graph Visualizations

The current graph visualizations (`convoviz/analysis/graphs.py`) are kinda lacking. Contributions that make them more meaningful, insightful, and visually appealing are highly appreciated.

---

## Development Setup

**Prerequisites**: Python 3.12+, [uv](https://github.com/astral-sh/uv)

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/convoviz.git
cd convoviz

# Install dependencies
uv sync

# Verify
uv run convoviz --help
uv run pytest
```

---

## Code Quality

Run the full quality gate before submitting:

```bash
uv run ruff check convoviz tests   # Lint
uv run ty check convoviz            # Type check
uv run pytest                       # Tests
```

Auto-fix lint issues: `uv run ruff check --fix convoviz tests`

---

## Testing

```bash
uv run pytest          # All tests
uv run pytest -x       # Stop on first failure
uv run pytest -v       # Verbose
```

When adding features, include tests for happy path, error cases, and edge cases.

### Regression Testing (Markdown Output)

While automated tests cover core logic, it's often helpful to manually verify the final Markdown output, especially when refactoring renderers or data models. 

**Finding Test Candidates**: If you need to find specific edge cases (like DALL-E images, reasoning chains, or complex branching) within your own export to test against, follow the [ChatGPT Export Discovery Guide](docs/dev/chatgpt-export-discovery.md).

#### 1. Generate Baseline and Current Outputs

Create a temporary directory to store and compare the results:

```bash
mkdir -p ./test-output

# Generate the baseline using the latest released version (via uvx)
rm -rf ./test-output/out1
uvx convoviz -z path/to/export.zip -o ./test-output/out1 --outputs markdown

# Generate the output from your local development environment
rm -rf ./test-output/out2
uv run convoviz -z path/to/export.zip -o ./test-output/out2 --outputs markdown
```

#### 2. Compare the Results

Use `git diff` to compare the two directories. The `--no-index` flag allows you to compare two paths on the filesystem even if they aren't part of a git repository.

```bash
# View a summary of which files changed and the extent of the changes
git diff --no-index --stat ./test-output/out1 ./test-output/out2

# Review the full diff of all changes
git diff --no-index ./test-output/out1 ./test-output/out2
```

#### 3. Targeted Testing

If you are investigating a specific issue, you may want to focus on a handful of noteworthy conversations. List the relative paths to these files (e.g., `Markdown/2023/07-July/My Chat.md`) in a text file named `conversation_list.txt`, then run a loop to diff them individually:

```bash
while read p; do
    git diff --no-index "./test-output/out1/$p" "./test-output/out2/$p"
done < conversation_list.txt
```

> [!TIP]
> For a much more readable and colorful diff experience, consider using [delta](https://github.com/dandavison/delta).

---

## Submitting Changes

1. Create a branch: `git checkout -b feature/your-feature`
2. Make focused commits
3. Run the quality gate (must pass)
4. Push and open a PR

---

## Architecture Quick Reference

```
convoviz/
├── cli.py          # CLI entrypoint
├── config.py       # Configuration models
├── pipeline.py     # Main processing flow
├── models/         # Pydantic data models (no I/O)
├── renderers/      # Markdown/YAML output (no disk writes)
├── io/             # All file operations
└── analysis/       # Graphs and word clouds
```

Key files to understand first:
- `convoviz/pipeline.py` — main processing flow
- `convoviz/config.py` — configuration options
- `docs/dev/HANDOFF.md` — full project context
