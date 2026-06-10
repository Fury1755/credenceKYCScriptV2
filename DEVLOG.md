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

## 2026-06-02
- refactored functions into 'core', 'boundary' and 'orchestration' folders

## 2026-06-03
- created 'pdf_processing.py' and 'pdf_io.py': parses pdfs using pdfplumber
- implemented recursive folder searching for business files
- switched to cloakbrowser to bypass bot detection

## 2026-06-04
- added 'search.py': searches for individuals and updates results
- added 'upload_excel' and 'append_excel': writes results to excel file
The script is now functional!

## 2026-06-05
- deployed and tested the script (3 times faster than v1)
- patched logic bugs in 'pdf_procesing.py'
- created 'test_string_helpers.py': first unit test using pytest and hypothesis

## 2026-06-06
- completed writing property tests for 'src/core/string_helpers.py' and patched exposed weaknesses (duplicates, falsy inputs)

## 2026-06-09
- added ruff: pre-commit hooks
- created 'test_sharepoint_clients': unit tests for sharepoint_client
- created 'sharepoint_client_parser.py': refactored sharepoint_client

## 2026-07-09
- created 'pdf_scraping/': scrapes pdfs
- created 'test_walk_folder_contents.py' and 'walk_folder_contents.py': more unit tests/factories for sharepoint_client
- refactored 'sharepoint_client.py': better organization, SRP
