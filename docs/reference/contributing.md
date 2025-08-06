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

[Home](/) > [Reference](reference/) > Contributing

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

## :material-rocket: Getting Started

### Quick Setup
1. **Fork** the repository on GitHub
2. **Install** MkDocs: `pip install -r requirements.txt`  
3. **Test locally**: `mkdocs serve` (access at http:/127.0.0.1:8000)
4. **Make changes** and verify they render correctly
5. **Submit** a pull request

## :material-format-list-checks: Contribution Process

| Step | Action | Details |
|------|--------|---------|
| 🔍 **1. Research** | Check existing issues | Review [open issues](https:/github.com/deepaucksharma/DStudio/issues/) and ongoing work |
| 🔧 **2. Setup** | Fork and clone repository | Create your development environment |
| ✏️ **3. Create** | Make your changes | Follow our quality standards (see below) |
| 🧪 **4. Test** | Verify locally | Run `mkdocs serve` and check all changes |
| 📤 **5. Submit** | Create pull request | Use our template and checklist |

### Quality Standards Checklist

!!! success "All contributions must meet these standards"
    
    **Technical Requirements**
    - [ ] Follows existing markdown formatting and style
    - [ ] Includes proper metadata (title, description, tags)
    - [ ] All links work correctly (no broken references)
    - [ ] Diagrams use consistent Mermaid syntax
    - [ ] Builds successfully with `mkdocs build`
    
    **Content Requirements**
    - [ ] Technically accurate and current
    - [ ] Uses clear, concise language
    - [ ] Includes relevant examples or diagrams
    - [ ] Cross-references related concepts appropriately
    - [ ] Maintains consistent terminology with glossary

### Pull Request Template

When submitting a PR, please include:

| Section | Required Info |
|---------|---------------|
| **Description** | Clear summary of what changed and why |
| **Type** | Bug fix, new feature, documentation, or performance |
| **Testing** | Confirmation that `mkdocs serve` works locally |
| **Self-Review** | You've checked your own changes thoroughly |

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

### Visual Content Guidelines

!!! tip "Diagrams and Images"
    
    **Preferred**: Use Mermaid diagrams for consistency
    ```mermaid
    graph LR
        A[Component A] --> B[Component B]
        B --> C[Component C]
    ```
    
    **Requirements**:
    - Use consistent color schemes and styling
    - Include alt text for accessibility  
    - Keep file sizes reasonable (<1MB for images)
    - Use SVG format when possible
    - Test rendering on different screen sizes

### Code Examples

!!! example "Code Standards"
    
    ```python
    # Use clear, runnable examples
    def example_function():
        """Include docstrings"""
        # Add helpful comments
        return "result"
    ```
    
    **Requirements**:
    - Include appropriate language hints
    - Keep examples focused and practical
    - Test all code for accuracy
    - Use realistic variable names and scenarios

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

- :material-github: [Open an Issue](https:/github.com/deepaucksharma/DStudio/issues/)
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
[:material-arrow-left: Recipe Cards](reference/recipe-cards/) | 
[:material-arrow-up: Reference](reference/) | 
[:material-arrow-right: Home](/)
</div>