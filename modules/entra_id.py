import os
import json
import requests
from msal import ConfidentialClientApplication
from dotenv import load_dotenv

load_dotenv()

# Load credentials from .env
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
TENANT_ID = os.getenv("AZURE_TENANT_ID")

if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID]):
    raise EnvironmentError("Azure AD credentials not found in .env")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]

app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
)

def _get_token():
    """Acquire a token using client credentials flow."""
    result = app.acquire_token_silent(SCOPES, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=SCOPES)
    if "access_token" not in result:
        raise Exception(f"Could not obtain token: {result.get('error_description')}")
    return result["access_token"]

BASE_URL = "https://graph.microsoft.com/v1.0"

def _graph_request(method: str, endpoint: str, json_body=None, params=None):
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{BASE_URL}{endpoint}"
    response = requests.request(method, url, headers=headers, json=json_body, params=params)
    if not response.ok:
        raise Exception(f"Graph request failed [{response.status_code}]: {response.text}")
    return response.json()

# ---------- Public functions ----------

def create_test_user(display_name: str = "Test User", user_principal_name: str = None, password: str = "TempP@ssw0rd!"):
    """Create a test user in Entra ID.
    If `user_principal_name` is omitted, we derive it from the tenant's default domain.
    """
    # Resolve default domain
    tenant_info = _graph_request("GET", "/organization")
    default_domain = tenant_info["value"][0]["verifiedDomains"][0]["name"]
    if not user_principal_name:
        user_principal_name = f"testuser@{default_domain}".lower()
    payload = {
        "accountEnabled": True,
        "displayName": display_name,
        "mailNickname": display_name.replace(" ", "").lower(),
        "userPrincipalName": user_principal_name,
        "passwordProfile": {"forceChangePasswordNextSignIn": False, "password": password},
    }
    result = _graph_request("POST", "/users", json_body=payload)
    return result

def delete_user_by_display_name(display_name: str):
    """Delete a user matching the given display name. Returns True if deleted."""
    users = _graph_request("GET", "/users", params={"$filter": f"displayName eq '{display_name}'"})
    if not users.get("value"):
        raise Exception(f"No user found with display name '{display_name}'")
    # If multiple, delete the first one
    user_id = users["value"][0]["id"]
    _graph_request("DELETE", f"/users/{user_id}")
    return True

def list_users():
    """Return a list of all users with basic licence information."""
    users = _graph_request("GET", "/users?$select=id,displayName,userPrincipalName")
    # Fetch licences for each user
    licences = _graph_request("GET", "/subscribedSkus?$select=skuId,prePaidUnits,skuPartNumber")
    sku_map = {item["skuId"]: item["skuPartNumber"] for item in licences.get("value", [])}
    # For each user, get assigned licenses
    detailed = []
    for u in users.get("value", []):
        lic = _graph_request("GET", f"/users/{u['id']}/licenseDetails?$select=skuId")
        lic_names = [sku_map.get(l["skuId"], l["skuId"]) for l in lic.get("value", [])]
        detailed.append({"displayName": u["displayName"], "userPrincipalName": u["userPrincipalName"], "licenses": lic_names})
    return detailed

def assign_role_to_user(user_principal_name: str, role_name: str):
    """Assign a directory role (e.g., 'User Administrator') to a user."""
    # Find role definition
    roles = _graph_request("GET", "/directoryRoles?$filter=displayName eq '{role_name}'".format(role_name=role_name))
    if not roles.get("value"):
        # Role may need activation first
        role_templates = _graph_request("GET", "/directoryRoleTemplates?$filter=displayName eq '{role_name}'".format(role_name=role_name))
        if not role_templates.get("value"):
            raise Exception(f"Role template '{role_name}' not found")
        template_id = role_templates["value"][0]["id"]
        # Activate role
        activation = _graph_request("POST", "/directoryRoles", json_body={"roleTemplateId": template_id})
        role_id = activation["id"]
    else:
        role_id = roles["value"][0]["id"]
    # Find user id
    user = _graph_request("GET", f"/users?$filter=userPrincipalName eq '{user_principal_name}'")
    if not user.get("value"):
        raise Exception(f"User '{user_principal_name}' not found")
    user_id = user["value"][0]["id"]
    # Assign role
    _graph_request("POST", f"/directoryRoles/{role_id}/members/$ref", json_body={"@odata.id": f"{BASE_URL}/users/{user_id}"})
    return True
