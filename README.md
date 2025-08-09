# DStudio

## Dependency Update Procedure

To update the pinned dependencies used for building the documentation site:

1. Review the desired versions for each package.
2. Edit `requirements.txt` and adjust the version numbers accordingly.
3. Install the updated dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the pre-commit checks for the modified files:
   ```bash
   pre-commit run --files requirements.txt README.md
   ```
5. Rebuild the documentation to verify everything works:
   ```bash
   mkdocs build
   ```