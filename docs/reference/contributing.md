---
title: Contributing Guide
description: How to contribute to The Compendium of Distributed Systems
icon: material/account-multiple
search:
  boost: 0.8
tags:
  - contributing
  - community
  - guidelines
---

# Contributing Guide

[Home](/) > [Reference](/reference/) > Contributing

!!! abstract "Join Our Community"
    The Compendium is a community-driven resource. We welcome contributions that help others learn distributed systems from first principles.

## :material-handshake: Ways to Contribute

<div class="grid cards" markdown>

- :material-file-document-edit:{ .lg .middle } **Content Improvements**
    
    ---
    
    - Fix typos and errors
    - Clarify explanations
    - Add missing details
    - Update outdated information

- :material-file-plus:{ .lg .middle } **New Content**
    
    ---
    
    - Case studies from production
    - Pattern implementations
    - Exercise solutions
    - Real-world examples

- :material-bug:{ .lg .middle } **Bug Reports**
    
    ---
    
    - Broken links
    - Incorrect code examples
    - Rendering issues
    - Navigation problems

- :material-translate:{ .lg .middle } **Translations**
    
    ---
    
    - Translate key concepts
    - Localize examples
    - Cultural adaptations
    - Review translations

</div>

## :material-format-list-checks: Contribution Process

### 1. Before You Start

!!! tip "Check First"
    - Review existing [issues](https://github.com/deepaucksharma/DStudio/issues)
    - Check if your contribution is already being worked on
    - For major changes, open an issue for discussion first

### 2. Making Changes

```bash
# Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/DStudio.git
cd DStudio

# Create a feature branch
git checkout -b feature/your-contribution

# Make your changes
# Test locally with: mkdocs serve

# Commit with clear message
git commit -m "Add: Clear description of change"
```

### 3. Submission Guidelines

!!! warning "Quality Standards"
    
    All contributions must:
    
    - Follow existing formatting and style
    - Include proper navigation (breadcrumbs, prev/next)
    - Add appropriate tags and metadata
    - Pass build tests
    - Be technically accurate

### 4. Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tested locally with `mkdocs serve`
- [ ] Verified navigation works
- [ ] Checked responsive design

## Checklist
- [ ] Follows style guidelines
- [ ] Self-review completed
- [ ] No broken links
```

## :material-pencil: Content Guidelines

### Writing Style

!!! info "Style Guide"
    
    - **Clear and Concise**: Avoid unnecessary jargon
    - **Examples First**: Lead with concrete examples
    - **Visual When Possible**: Use diagrams and tables
    - **Progressive Disclosure**: Simple → Complex
    - **Cross-References**: Link to related concepts

### Page Structure

Every page should follow this structure:

```markdown
---
title: Page Title
description: SEO description
tags:
  - relevant
  - tags
---

# Page Title

[Breadcrumb navigation]

!!! abstract "Overview"
    Brief summary

## Main Content

...

## Related Topics

...

---

[Navigation footer]
```

### Code Examples

!!! example "Code Standards"
    
    ```python
    # Use clear, runnable examples
    def example_function():
        """Include docstrings"""
        # Add helpful comments
        return "result"
    ```
    
    - Include language hints
    - Keep examples focused
    - Show both good and bad practices
    - Test all code

## :material-shield-check: Legal

### Contributor License Agreement

By contributing, you agree that:

- Your contributions are your original work
- You grant us license to use your contributions
- Your contributions are provided "as is"

### Code of Conduct

!!! quote "Community Standards"
    
    - **Be Respectful**: Welcoming to all skill levels
    - **Be Constructive**: Focus on improving content
    - **Be Patient**: Everyone is learning
    - **Be Professional**: Keep discussions technical

## :material-help-circle: Getting Help

Need assistance?

- :material-github: [Open an Issue](https://github.com/deepaucksharma/DStudio/issues)
- :material-chat: Join discussions in issues/PRs
- :material-email: Contact maintainers (see README)

## :material-star: Recognition

Contributors are recognized in:

- Git history
- Contributors page
- Release notes
- Special thanks section

## :material-rocket: Start Contributing

Ready to contribute?

1. Pick an area that interests you
2. Start small (typo fixes are welcome!)
3. Read existing content for style
4. Submit your first PR

Thank you for helping make distributed systems knowledge accessible to everyone!

---

<div class="page-nav" markdown>
[:material-arrow-left: Recipe Cards](/reference/recipe-cards/) | 
[:material-arrow-up: Reference](/reference/) | 
[:material-arrow-right: Home](/)
</div>