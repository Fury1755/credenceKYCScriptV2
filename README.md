## Purpose
KYC (Know-Your-Client) is a background check conducted on clients to prevent financial crimes.
It extracts company data from an excel checking sheet, retrieves the latest ACRA business profiles from the company SharePoint, performs a Google search on individuals, takes a screenshot, uploads the evidence to SharePoint and logs the progress back onto the excel sheet.

## Current status
The script is functional but tangled. For example, the "SharePointClient" class, which has grown to become a 'god' object, containing both API-related methods and core processing logic. A refactor is planned to improve maintainability and separation of concerns.

## Technologies
playwright - framework that automates browser actions
SharePoint REST API - folder navigation and retrieval
cloakbrowser - the actual playwright fork used
pdfplumber - for extracting and parsing business profiles
openpyxl - for reading from and updating the excel checking sheet
rapidfuzz - for fuzzy matching used in folder navigation

## Architecture
boundary - handles I/O and API calls (file downloads, folder navigation)
core - pure logic (parsing urls as strings, pdf parsing, reading/writing to excel files)
orchestration - glue code
SharePointClient - a class that attempted to encapsulate API logic but grew too large and became entangled in processing logic

## Learning objectives
Through this project, I aim to learn and implement:
- commit hygiene
- defensive programming for I/O modules
- Design by Contract for core modules
- Encapsulation with SharePointClient and its (not yet) subclasses