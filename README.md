
Ren Agent

Ren is a personal IT operations agent built with Google ADK and Gemini. It connects to a live Windows Server 2022 environment and automates real IT support tasks — user provisioning, incident management, and audit logging.

What Ren Does

	•	Creates, deletes, resets, and lists Active Directory users in a Windows Server 2022 VM via WinRM
	•	Raises, updates, and closes ServiceNow incidents via the Table REST API
	•	Logs every operation automatically to an Excel workbook with timestamp and outcome

Provisioning Workflow

One conversational command triggers the full workflow:

	1.	AD user created in Windows Server 2022 (corp.local domain) via WinRM
	2.	ServiceNow incident raised and linked to the provisioning action
	3.	Action logged to Excel audit trail with date, type, and result

Supporting Scripts

Standalone Python scripts for common IT support tasks:

	•	scripts/entra_id.py — Microsoft Entra ID user lookup, licence check, and account disable via Graph API
	•	scripts/network_checker.py — ping, DNS lookup, port check
	•	scripts/system_health.py — CPU, memory, and disk usage reporting

Lab Environment

	•	Windows Server 2022 — Active Directory, DNS, DHCP
	•	Windows 11 VM — managed remotely via RDP
	•	VMware Workstation — host for both VMs
	•	ServiceNow Developer Instance — live ticketing environment
	•	Microsoft Entra ID — cloud identity management via Graph API

Tech Stack

	•	Python 3.11
	•	Google ADK 2.1.0
	•	Gemini
	•	pywinrm
	•	microsoft-graph / requests
	•	openpyxl
	•	python-dotenv

Notes

.env contains all credentials and is excluded from this repo. Never push credentials to GitHub.

Change Python version to 3.11 once that’s installed. Tell your IDE AI to replace the full README with this. Then push to GitHub.
## Screenshots

![User in AD](screenshots/User%20in%20AD.jpeg)
![User Created](screenshots/User%20Created.jpeg)


