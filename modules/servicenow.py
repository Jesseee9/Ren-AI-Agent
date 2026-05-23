import requests
import os
from dotenv import load_dotenv

load_dotenv()

SN_INSTANCE = os.getenv("SN_INSTANCE")
SN_USERNAME = os.getenv("SN_USERNAME")
SN_PASSWORD = os.getenv("SN_PASSWORD")

def create_incident(short_description: str, details: str) -> str:
    """Create a ServiceNow incident and return the ticket number."""
    url = f"{SN_INSTANCE}/api/now/table/incident"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "short_description": short_description,
        "description": details,
        "urgency": "3",
        "impact": "3"
    }
    response = requests.post(url, json=payload, auth=(SN_USERNAME, SN_PASSWORD), headers=headers)
    if response.status_code == 201:
        ticket = response.json()["result"]["number"]
        return f"Incident created: {ticket}"
    return f"ERROR: {response.status_code} - {response.text}"

def update_incident(ticket_number: str, update_note: str) -> str:
    """Update an existing ServiceNow incident with a work note."""
    url = f"{SN_INSTANCE}/api/now/table/incident"
    params = {"sysparm_query": f"number={ticket_number}"}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    search = requests.get(url, params=params, auth=(SN_USERNAME, SN_PASSWORD), headers=headers)
    results = search.json().get("result", [])
    if not results:
        return f"ERROR: Ticket {ticket_number} not found"
    sys_id = results[0]["sys_id"]
    patch_url = f"{url}/{sys_id}"
    payload = {"work_notes": update_note}
    response = requests.patch(patch_url, json=payload, auth=(SN_USERNAME, SN_PASSWORD), headers=headers)
    if response.status_code == 200:
        return f"Incident {ticket_number} updated successfully"
    return f"ERROR: {response.status_code} - {response.text}"

def close_incident(ticket_number: str, resolution_note: str) -> str:
    """Close a ServiceNow incident with a resolution note."""
    url = f"{SN_INSTANCE}/api/now/table/incident"
    params = {"sysparm_query": f"number={ticket_number}"}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    search = requests.get(url, params=params, auth=(SN_USERNAME, SN_PASSWORD), headers=headers)
    results = search.json().get("result", [])
    if not results:
        return f"ERROR: Ticket {ticket_number} not found"
    sys_id = results[0]["sys_id"]
    patch_url = f"{url}/{sys_id}"
    payload = {
        "state": "6",
        "close_code": "Solved (Permanently)",
        "close_notes": resolution_note
    }
    response = requests.patch(patch_url, json=payload, auth=(SN_USERNAME, SN_PASSWORD), headers=headers)
    if response.status_code == 200:
        return f"Incident {ticket_number} closed successfully"
    return f"ERROR: {response.status_code} - {response.text}"
