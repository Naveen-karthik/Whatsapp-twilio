import json
import os

from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise RuntimeError("MISTRAL_API_KEY is not configured")


client = Mistral(api_key=MISTRAL_API_KEY)

MODEL = "mistral-small-latest"


SYSTEM_PROMPT = """
You are an intent extraction assistant for a hospital appointment
booking chatbot.

Your job is ONLY to understand the user's message and return structured
JSON.

Do not invent information.

Return exactly this structure:

{
    "intent": "string",
    "value": "string",
    "confidence": 0.0
}

Possible intents:

WELCOME_START
WORKING_HOURS
EXIT
PATIENT_NAME
SELECT_DOCTOR
SELECT_APPOINTMENT_TYPE
SELECT_DATE
SELECT_TIME
RESCHEDULE
UNKNOWN

Available doctors:

- doctor_shalini = Dr. Shalini, Dermatologist
- doctor_raj = Dr. Raj, Pediatrician
- doctor_kumar = Dr. Kumar, Dental

Available appointment types:

- Initial Consultation
- Follow-up Consultation
- Virtual Meeting
- In-person Meeting

Available dates:

- Today
- Tomorrow
- Later

Available times:

- 11:00 AM
- 12:00 PM
- 2:00 PM
- 3:00 PM
- 5:00 PM

Rules:

1. If the user wants to start booking:
   intent = WELCOME_START
   value = "start"

2. If the user asks about hospital working hours:
   intent = WORKING_HOURS

3. If the user wants to exit or cancel:
   intent = EXIT

4. If the user provides a person's name:
   intent = PATIENT_NAME
   value = the person's name

5. If the user selects or describes Dr. Shalini:
   intent = SELECT_DOCTOR
   value = "doctor_shalini"

6. If the user selects or describes Dr. Raj:
   intent = SELECT_DOCTOR
   value = "doctor_raj"

7. If the user selects or describes Dr. Kumar:
   intent = SELECT_DOCTOR
   value = "doctor_kumar"

8. Map natural language appointment requests to the closest
   available appointment type.

9. Map date requests:
   today -> Today
   tomorrow -> Tomorrow
   later/future date -> Later

10. Map time requests to the closest exact available time.

11. If the user wants to change an existing appointment:
   intent = RESCHEDULE

12. Never invent a doctor, appointment type, date, or time.

13. If you cannot confidently understand the request:
   intent = UNKNOWN

Return JSON only.
"""


def understand_message(user_input: str, current_step: str):

    prompt = f"""
Current conversation step:

{current_step}

User message:

{user_input}

Understand the user's intent based on the current conversation step.

Return JSON only.
"""

    try:

        response = client.chat.complete(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_object"
            },
            temperature=0
        )

        content = response.choices[0].message.content

        result = json.loads(content)

        return result

    except Exception as error:

        print(f"Mistral error: {error}")

        return {
            "intent": "UNKNOWN",
            "value": "",
            "confidence": 0
        }