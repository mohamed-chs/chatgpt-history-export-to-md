# Next Steps for Convoviz

This document outlines remaining work, improvements, and future enhancements for the convoviz project after the January 2026 modernization.

## Immediate TODO

### 1. Update README.md
- [ ] Update Python version requirement to 3.12+
- [ ] Add development setup instructions with `uv`
- [ ] Document new module structure
- [ ] Add contributing guidelines

### 2. Remove Deprecated Files
- [ ] Delete `pyproject.toml.bak` (backup from migration)
- [ ] Clean up any `__pycache__` directories
- [ ] Review and update `playground.ipynb` for new API

### 3. Missing Tests
- [ ] Add tests for `convoviz/interactive.py` (currently untested due to user input)
- [ ] Add integration tests that run the full pipeline with real data
- [ ] Add tests for `analysis/graphs.py` output validation
- [ ] Add tests for `analysis/wordcloud.py` output validation

## Short-term Improvements

### Code Quality
- [ ] Add docstrings to all public functions (some are missing)
- [ ] Add `py.typed` marker for PEP 561 compliance (exists but verify)
- [ ] Consider adding `strict` mode to mypy configuration
- [ ] Add pre-commit hooks for automated linting/formatting

### Error Handling
- [ ] Add more specific exceptions for different failure modes
- [ ] Improve error messages with actionable suggestions
- [ ] Add logging throughout the application (currently uses `rich.console` only)

### Configuration
- [ ] Support loading config from TOML/YAML file
- [ ] Add environment variable support via `pydantic-settings`
- [ ] Add config validation with helpful error messages

## Medium-term Enhancements

### Features
- [ ] Add support for newer ChatGPT export formats (if changed)
- [ ] Add more visualization types (timeline, heatmap, etc.)
- [ ] Add export to other formats (HTML, PDF)
- [ ] Add conversation search/filter functionality
- [ ] Add support for conversation threading visualization

### Performance
- [ ] Profile the application to identify bottlenecks
- [ ] Consider parallel processing for large exports
- [ ] Add progress callbacks for library usage (not just CLI)
- [ ] Lazy load matplotlib/wordcloud for faster CLI startup

### API Improvements
- [ ] Add async support for I/O operations
- [ ] Create a proper public API surface in `__init__.py`
- [ ] Add builder pattern for configuration
- [ ] Consider adding a REST API or web interface

## Long-term Vision

### Packaging & Distribution
- [ ] Publish to PyPI
- [ ] Add GitHub Actions for CI/CD
- [ ] Add automated releases on tag
- [ ] Consider creating a standalone binary with PyInstaller

### Documentation
- [ ] Create proper documentation site (MkDocs/Sphinx)
- [ ] Add API reference documentation
- [ ] Add usage examples and tutorials
- [ ] Add architecture documentation

### Extensibility
- [ ] Plugin system for custom visualizations
- [ ] Support for other chat export formats (Claude, Gemini, etc.)
- [ ] Theming support for visualizations

## Technical Debt

### Known Issues
- `GraphConfig` is currently empty - needs fields for customization
- Font path resolution could be more robust
- Bookmarklet JSON loading has minimal error handling
- Some `# type: ignore` comments may need revisiting

### Refactoring Candidates
- `interactive.py` has long function - consider breaking up
- Duplicated field lists in `interactive.py` (YAML fields)
- Consider using `enum` for `AuthorRole` instead of `Literal`

## Dependencies to Watch

| Package | Current | Notes |
|---------|---------|-------|
| pydantic | 2.12+ | Major version changes may need migration |
| typer | 0.21+ | Watch for breaking changes |
| matplotlib | 3.9+ | Generally stable |
| wordcloud | 1.9+ | Untyped, may need stubs |
| nltk | 3.9+ | Stopwords may need updates |

## Notes

- The codebase was modernized in January 2026 from Python 3.9 to 3.12+
- Switched from TypedDict to Pydantic models for configuration
- Separated concerns: models are now pure data, rendering is separate
- All tests pass (70 tests as of modernization)
