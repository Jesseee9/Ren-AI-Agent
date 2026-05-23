# Ren Agent

A personal IT operations agent built with Google ADK 2.0.0 and Gemini. Ren automates real IT support tasks — creating Active Directory users, raising ServiceNow incidents, and logging every action to Excel.

## What Ren Can Do

- Create, delete, and manage AD users in a Windows Server VM via WinRM
- Raise, update, and close ServiceNow incidents via REST API
- Log every operation to an Excel workbook automatically

## Workflow

One command triggers the full IT provisioning workflow:

1. AD user created in Windows Server via WinRM
2. ServiceNow incident raised confirming completion
3. Action logged to Excel

## Supporting Scripts

Standalone diagnostic scripts for:
- Entra ID user lookup and licence checks
- Network diagnostics — ping, DNS, port checks
- System health — CPU, memory, disk

## Tech Stack

- Python 3.14
- Google ADK 2.0.0
- pywinrm
- requests
- openpyxl

## Screenshots

_(coming soon)_

## Author

Jesse Adejo
