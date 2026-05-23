import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from modules.lab_logger import log_session
from modules.ad_manager import create_ad_user
from modules.servicenow import create_incident

# Optional import of the Gemini SDK – if it fails we continue without AI features
try:
    from google.generativeai import configure
    configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    print(f"[!] Warning: Google GenerativeAI SDK not available – {e}")

import platform, getpass, sys

load_dotenv()


def log_lab_session(topic: str, description: str, completed: str, duration: str) -> str:
    "Log an IT lab practice session to Excel."
    return log_session(topic, description, completed, duration)

def system_info() -> str:
    "Return computer name, current user, and Python version."
    return f"{platform.node()}, {getpass.getuser()}, Python {sys.version.split()[0]}"

def provision_user_and_incident(first_name: str, last_name: str, password: str, incident_desc: str) -> str:
    "Create AD user, raise ServiceNow incident, and log the operation."
    try:
        user_msg = create_ad_user(first_name, last_name, password)
    except Exception as e:
        user_msg = f"AD creation error: {e}"
    try:
        incident_msg = create_incident(f"AD user {first_name} {last_name}", incident_desc)
    except Exception as e:
        incident_msg = f"Incident creation error: {e}"
    try:
        log_msg = log_session(
            topic="AD Provision",
            description=f"Created user {first_name} {last_name} and logged incident.",
            completed="yes",
            duration="0"
        )
    except Exception as e:
        log_msg = f"Logging error: {e}"
    return f"{user_msg}\n{incident_msg}\n{log_msg}"

root_agent = Agent(
    name="ren",
    model="gemini-2.0-flash",
    description="Ren is a personal IT operations assistant.",
    instruction="You are Ren, a professional IT operations assistant. Use the provided tools.",
    tools=[log_lab_session, system_info, provision_user_and_incident],
)

async def main() -> None:
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="ren", user_id="jesse", session_id="main")
    runner = Runner(agent=root_agent, app_name="ren", session_service=session_service)

    print("\nRen Agent — Online")
    print("Type your request or 'exit' to quit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        content = types.Content(
            role="user",
            parts=[types.Part(text=user_input)],
        )

        async for event in runner.run_async(
            user_id="jesse", session_id="main", new_message=content
        ):
            if event.is_final_response():
                print(f"\nRen: {event.response.text}\n")

if __name__ == "__main__":
    asyncio.run(main())