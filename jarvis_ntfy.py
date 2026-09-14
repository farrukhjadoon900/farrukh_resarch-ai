from __future__ import annotations

import json
import os
import time
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

NTFY_TOPIC = os.getenv("NTFY_TOPIC", "mfj-jarvis")
NTFY_BASE_URL = os.getenv("NTFY_BASE_URL", "https://ntfy.sh").rstrip("/")
NTFY_URL = f"{NTFY_BASE_URL}/{NTFY_TOPIC}"
NTFY_STREAM_URL = f"{NTFY_URL}/json"

# Optional: private/authenticated ntfy topic ke liye.
NTFY_USERNAME = os.getenv("NTFY_USERNAME", "")
NTFY_PASSWORD = os.getenv("NTFY_PASSWORD", "")

# Agar aap sirf apne account ko allow karna chahte hain.
JARVIS_USER_ID = os.getenv("JARVIS_USER_ID", "")


def ntfy_auth() -> tuple[str, str] | None:
    if NTFY_USERNAME and NTFY_PASSWORD:
        return NTFY_USERNAME, NTFY_PASSWORD
    return None


def publish_to_ntfy(message: str, title: str = "Jarvis") -> None:
    headers = {
        "Title": title,
        "Priority": "default",
        "Tags": "robot",
        "Content-Type": "text/plain; charset=utf-8",
    }

    response = httpx.post(
        NTFY_URL,
        content=message.encode("utf-8"),
        headers=headers,
        auth=ntfy_auth(),
        timeout=30.0,
    )
    response.raise_for_status()


def run_jarvis(command: str, user_id: str = "") -> str:
    """
    Yahan apne existing CrewAI Jarvis ko call kiya gaya hai.
    Agar aapke crew ka import/name different hai to sirf yeh function edit karein.
    """

    from jarvis.crew import JarvisCrew

    crew = JarvisCrew().crew()

    result = crew.kickoff(
        inputs={
            "command": command,
            "user_id": user_id,
        }
    )

    return str(result)


def extract_command(event: dict[str, Any]) -> tuple[str, str]:
    """
    Ntfy event se message aur user_id nikalta hai.
    """

    message = str(event.get("message", "")).strip()

    # Ntfy message ke andar optional JSON bhi allow hai:
    # {"command": "weather batao", "user_id": "abc"}
    try:
        parsed = json.loads(message)

        if isinstance(parsed, dict):
            command = str(
                parsed.get("command")
                or parsed.get("message")
                or parsed.get("text")
                or ""
            ).strip()

            user_id = str(parsed.get("user_id") or "").strip()
            return command, user_id

    except json.JSONDecodeError:
        pass

    return message, ""


def listen_forever() -> None:
    print(f"Jarvis ntfy topic listen kar raha hai: {NTFY_URL}")

    while True:
        try:
            with httpx.stream(
                "GET",
                NTFY_STREAM_URL,
                params={"poll": "1"},
                auth=ntfy_auth(),
                timeout=None,
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Ntfy connection events ignore karein.
                    if event.get("event") != "message":
                        continue

                    command, user_id = extract_command(event)

                    if not command:
                        continue

                    if JARVIS_USER_ID and user_id != JARVIS_USER_ID:
                        publish_to_ntfy(
                            "Unauthorized user. Command reject kar di gayi.",
                            title="Jarvis Security",
                        )
                        continue

                    try:
                        publish_to_ntfy(
                            "Command receive ho gayi. Main process kar raha hoon...",
                            title="Jarvis",
                        )

                        answer = run_jarvis(command, user_id)

                        if not answer.strip():
                            answer = "Jarvis ne koi response return nahi kiya."

                        publish_to_ntfy(answer, title="Jarvis Response")

                    except Exception as exc:
                        error_message = (
                            "Jarvis command run karte waqt error aaya:\n"
                            f"{type(exc).__name__}: {exc}"
                        )
                        publish_to_ntfy(error_message, title="Jarvis Error")

        except Exception as exc:
            print(f"ntfy connection error: {exc}")
            print("5 seconds baad reconnect ho raha hai...")
            time.sleep(5)


if __name__ == "__main__":
    listen_forever()
