# Pandoc PDF Guide (Typst)

This guide covers how Convoviz markdown outputs can be rendered to PDF using Quarto, with a Typst workflow.

## Why Typst

Quarto supports a dedicated `format: typst` output for PDF generation. Typst provides fast, modern PDF rendering and its own citation processing when using the Typst format.

## Recommended Frontmatter

Convoviz can inject PDF frontmatter when you use the `pandoc` markdown flavor.

```yaml
---
format: typst
---
```

## Rendering with Quarto

If your markdown contains the frontmatter above, you can render to PDF directly:

```bash
quarto render path/to/file.md --to typst
```

You can also render without the `--to` flag if the format is specified in the frontmatter:

```bash
quarto render path/to/file.md
```

## Convoviz Config Integration

In `config.toml` you can adjust PDF settings under `conversation.pandoc_pdf`:

```toml
[conversation.pandoc_pdf]
enabled = true
```

This frontmatter is only injected when the markdown flavor is `pandoc`.

## YAML Separator Safety

When using the `pandoc` markdown flavor, Convoviz indents any line that starts with
`---` after the YAML frontmatter header. This prevents Quarto/Pandoc from treating
content separators as a second metadata block while preserving horizontal rules.

## WebP Assets

When using the `pandoc` markdown flavor, Convoviz will attempt to convert WebP
assets to PNG during export. This keeps Quarto/Pandoc PDF generation from
failing on unsupported WebP files.
