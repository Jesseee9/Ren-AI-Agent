# Troubleshooting

## WinRM Connection Timeout
**Error:** `TypeError: expected string or bytes-like object, got 'None'`  
**Cause:** VM_HOST not loading from .env  
**Fix:** Ensure .env has no spaces around `=` signs. Use IP 192.168.128.130 not 192.168.10.10

## Wrong VM IP
**Cause:** Windows Server has two network adapters  
**Fix:** Use Ethernet1 address (192.168.128.130) — this is reachable from the host machine

## ServiceNow 401 Unauthorized
**Cause:** Special characters in password being mangled by dotenv  
**Fix:** Reset PDI password to alphanumeric only, update .env

## ADK Tool Compatibility Errors
**Cause:** Python 3.14 not fully supported by google-adk 2.0.0  
**Fix:** Ensure all tool functions have explicit type hints, single line docstrings, no bool parameters, return strings only
