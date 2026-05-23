import winrm
import os
import socket
from dotenv import load_dotenv

load_dotenv()

VM_HOST = os.getenv("VM_HOST")
VM_USERNAME = os.getenv("VM_USERNAME")
VM_PASSWORD = os.getenv("VM_PASSWORD")

def run_ps(script: str) -> str:
    """Run a PowerShell script on the Windows Server VM via WinRM.
    Returns an error string if required environment variables are missing or the host is unreachable."""
    # Validate credentials
    if not VM_HOST or not VM_USERNAME or not VM_PASSWORD:
        return "ERROR: Missing WinRM credentials (VM_HOST, VM_USERNAME, VM_PASSWORD)."
    # Detect placeholder values
    if any(v.startswith("YOUR_") for v in (VM_HOST, VM_USERNAME, VM_PASSWORD)):
        return "ERROR: Please replace placeholder VM_HOST, VM_USERNAME, VM_PASSWORD in .env with real values."
    # Quick connectivity check (port 5985 is default WinRM HTTP port)
    try:
        with socket.create_connection((VM_HOST, 5985), timeout=5):
            pass
    except OSError as e:
        return f"ERROR: Cannot reach WinRM endpoint at {VM_HOST}:5985 – {e}. Ensure the VM is reachable, WinRM is enabled, and firewall allows port 5985."
    # Proceed with WinRM session
    session = winrm.Session(
        VM_HOST,
        auth=(VM_USERNAME, VM_PASSWORD),
        transport="ntlm"
    )
    result = session.run_ps(script)
    if result.status_code != 0:
        return f"ERROR: {result.std_err.decode()}"
    return result.std_out.decode().strip()

def create_ad_user(first_name: str, last_name: str, password: str) -> str:
    """Create an AD user in the corp.local domain."""
    username = f"{first_name.lower()}.{last_name.lower()}"
    script = f"""
    New-ADUser `
        -Name \"{first_name} {last_name}\" `
        -GivenName \"{first_name}\" `
        -Surname \"{last_name}\" `
        -SamAccountName \"{username}\" `
        -UserPrincipalName \"{username}@corp.local\" `
        -AccountPassword (ConvertTo-SecureString \"{password}\" -AsPlainText -Force) `
        -Enabled $true `
        -Path \"CN=Users,DC=corp,DC=local\"
    """
    result = run_ps(script)
    if "ERROR" in result:
        return f"Failed to create user {username}: {result}"
    return f"User {username} created successfully in corp.local"

def delete_ad_user(username: str) -> str:
    """Delete an AD user by SamAccountName."""
    script = f'Remove-ADUser -Identity "{username}" -Confirm:$false'
    result = run_ps(script)
    if "ERROR" in result:
        return f"Failed to delete user {username}: {result}"
    return f"User {username} deleted successfully"

def reset_ad_password(username: str, new_password: str) -> str:
    """Reset an AD user's password."""
    script = f"""
    Set-ADAccountPassword -Identity \"{username}\" `
        -NewPassword (ConvertTo-SecureString \"{new_password}\" -AsPlainText -Force) `
        -Reset
    """
    result = run_ps(script)
    if "ERROR" in result:
        return f"Failed to reset password for {username}: {result}"
    return f"Password reset successfully for {username}"

def list_ad_users() -> str:
    """List all AD users in the domain."""
    script = "Get-ADUser -Filter * | Select-Object Name, SamAccountName, Enabled | Format-Table -AutoSize"
    return run_ps(script)
