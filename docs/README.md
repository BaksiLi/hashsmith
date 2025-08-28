# Documentation

This directory contains documentation for the HashSmith project.

## Structure

- `wiki/` - GitHub wiki pages (auto-synced via GitHub Actions)
  - `Home.md` - Main wiki landing page
  - `Design-Rationale.md` - Core concepts and mathematical model
  - `Transforms.md` - Available transformations and usage patterns
  - `Examples.md` - Practical usage examples and patterns

## GitHub Wiki Integration

The `wiki/` directory is automatically synced to the GitHub wiki repository via GitHub Actions. When you:

1. Make changes to files in `docs/wiki/`
2. Push to the main branch
3. The GitHub Action automatically updates the wiki repository

This allows you to:
- Edit wiki content locally in your preferred editor
- Use version control for wiki changes
- Automatically sync changes to the live wiki

## Manual Wiki Updates

If you need to manually update the wiki, you can:

1. Clone the wiki repository: `git clone https://github.com/BaksiLi/hashsmith.wiki.git`
2. Make your changes
3. Commit and push: `git add . && git commit -m "Update wiki" && git push`

## Local Development

For local documentation development, you can:

1. Edit files in `docs/wiki/`
2. Preview changes locally
3. Push to trigger automatic wiki sync

The wiki files use standard Markdown with GitHub wiki-specific features like `[[Internal Links]]`.
