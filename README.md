## Purpose
KYC (Know-Your-Client) is a background check conducted on clients to prevent financial crimes.
The process is lengthy and cannot be fully automated as a human is required to verify the search results for each client, but we can partially automate the process.

The manual process is as follows:

1. Extract company data from an excel checking sheet
2. Retrieve the latest ACRA business profiles from the company SharePoint
3. Perform a Google/Baidu search on individuals
4. Take a screenshot
5. Rename the screenshot to the appropriate name
6. Upload the evidence to SharePoint in the appropriate folders
7. Log the progress back onto the excel sheet

With this script, steps 1 through 3 and 5 through 7 are automated, reducing the time taken from ~10 minutes per client to ~1-2 minutes per client.

## Current status
This project is feature complete.

As KYC is done once every 3 years and is usually delegated to juniors/interns (like me), the time costs of writing it to be reliably deployable on other machines outweigh the benefits. However, I have used this as an opportunity to learn about best practices for writing reliable code.

## Technologies
- playwright - framework that automates browser actions
- SharePoint REST API - folder navigation and retrieval
- cloakbrowser - the actual playwright fork used
- pdfplumber - for extracting and parsing business profiles
- openpyxl - for reading from and updating the excel checking sheet
- rapidfuzz - for fuzzy matching used in folder navigation

## Architecture
- boundary - handles I/O and API calls (file downloads, folder navigation)
- core - pure logic (parsing urls as strings, pdf parsing, reading/writing to excel files)
- orchestration - glue code
- SharePointClient - a class that encapsulates the state of a folder/file in SharePoint.

## Learning objectives
Through this project, I have learned and implemented:
- commit hygiene
- defensive programming for I/O modules
- Design by Contract for core modules
- Encapsulation with SharePointClient and its subclass
- unit testing (insufficient for the purposes of this script, but learned)