# Hello World MkDocs

A simple Hello World documentation site built with MkDocs and Material for MkDocs theme.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
mkdocs serve
```

Visit http://127.0.0.1:8000 to view the site.

## Project Structure

```
.
├── docs/
│   ├── index.md          # Homepage
│   └── about.md          # About page
├── mkdocs.yml            # MkDocs configuration
├── requirements.txt      # Python dependencies
├── CLAUDE.md            # Claude Code instructions
├── CONTRIBUTING.md      # Contribution guidelines
└── README.md            # This file
```

## Features

- **Material Design**: Beautiful Material for MkDocs theme
- **Dark Mode**: Automatic light/dark theme switching
- **Search**: Full-text search functionality
- **Responsive**: Works on all devices
- **Fast**: Static site generation for quick loading

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server (with hot reload)
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages (optional)
mkdocs gh-deploy
```

## Customization

Edit the following files to customize your site:

- `mkdocs.yml` - Site configuration and navigation
- `docs/index.md` - Homepage content  
- `docs/about.md` - About page content
- Add more `.md` files in `docs/` and update navigation in `mkdocs.yml`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is open source and available under the [MIT License](LICENSE).