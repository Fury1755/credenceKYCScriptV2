# DEVLOG

## 2026-05-26
- Set up uv-venv, ruff and pylint
- Created 'config.py' using .env
- Created 'main.py' using Playwright's persistent context

## 2026-05-27
- Created 'excel_io.py': downloads and uploads Excel files via REST api
- Created 'excel_processing.py': modifies workbooks using openpyxl
- Implemented code quality standards (PEP 8, docstrings)

## 2026-05-28
- Created 'SharePoint_types.py': provides static analysis for server responses
- Created 'helper_functions.py': logs server rate limits and parses urls
- Implemented basic error logging using the logging module

## 2026-05-29
- Created 'navigation_functions.py': fetches subfolders from a SharePoint url
- Created 'response_helpers.py': automatic rate throttling
- Created 'string_helpers.py': fuzzy matching functions using the rapidfuzz library

## 2026-05-31
- created 'orchestration.py': orchestrates SharePoint navigation
- refactored functions to 'get_folders_and_files': more generic function calls
- created 'README.md'
- rewrote I/O functions to take browser links as arguments: more user-friendly

## 2026-06-01
- created 'sharepoint_client.py': encapsulation of API related calls within a class
- created 'sharepoint_exceptions.py' and implemented defensive programming for I/O

## 2026-05-02
- refactored functions into 'core', 'boundary' and 'orchestration' folders