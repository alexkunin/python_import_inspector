# Python Import Inspector

Python Import Inspector is a utility that analyzes the import dependencies within a Python project. It identifies local, third-party, namespaced, unknown, and missing imports, and generates a report summarizing the findings.

## Features

- **Recursive File Scanning:** Scans the specified directory and subdirectories for Python files.
- **Import Analysis:** Extracts and classifies import statements from each Python file.
- **Reporting:** Provides a detailed report on the status of imports, highlighting unimported modules and problematic imports.

## Usage

Just run it inside your project directory.

## Sample report

```
file1.py: not imported
file1.py: namespaced imports: ['google.cloud']
file2.py: not imported
dir1/file3.py: unknown imports: ['torch', 'clip']
dir2/file4.py: missing imports: ['playwright.async_api']
```
