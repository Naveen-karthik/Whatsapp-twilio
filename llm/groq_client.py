import json
import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

MODEL = "llama-3.1-8b-instant"


SYSTEM_PROMPT = """
You are an intent extraction assistant for a hospital appointment
booking chatbot.

Your job is ONLY to understand the user's message and return JSON.

Return exactly:

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

doctor_shalini = Dr. Shalini, Dermatologist
doctor_raj = Dr. Raj, Pediatrician
doctor_kumar = Dr. Kumar, Dental


Available appointment types:

Initial Consultation
Follow-up Consultation
Virtual Meeting
In-person Meeting


Available dates:

Today
Tomorrow
Later


Available times:

11:00 AM
12:00 PM
2:00 PM
3:00 PM
5:00 PM


Rules:

1. If the user wants to start booking:
   intent = WELCOME_START
   value = "start"

2. If the user asks about working hours:
   intent = WORKING_HOURS
   value = "working_hours"

3. If the user wants to exit or cancel:
   intent = EXIT
   value = "exit"

4. If the user provides a patient's name:
   intent = PATIENT_NAME
   value = the patient's name

5. If the user wants Dr. Shalini or describes a dermatologist/skin doctor:
   intent = SELECT_DOCTOR
   value = "doctor_shalini"

6. If the user wants Dr. Raj or describes a pediatrician/children's doctor:
   intent = SELECT_DOCTOR
   value = "doctor_raj"

7. If the user wants Dr. Kumar or describes a dental/dentist doctor:
   intent = SELECT_DOCTOR
   value = "doctor_kumar"

8. Map appointment requests to the available appointment types.

9. Map:
   today -> Today
   tomorrow -> Tomorrow
   later/future -> Later

10. Map time requests to one of the available times.

11. If the user wants to change an existing appointment:
   intent = RESCHEDULE
   value = "reschedule"

12. Never invent doctors, appointment types, dates, or times.

13. If the meaning cannot be determined:
   intent = UNKNOWN
   value = ""

Return JSON only.
"""


def understand_message(user_input: str, current_step: str):

    if not client:
        print("GROQ_API_KEY is not configured")

        return {
            "intent": "UNKNOWN",
            "value": "",
            "confidence": 0
        }

    prompt = f"""
Current conversation step:
{current_step}

User message:
{user_input}

Understand the user's intent based on the current conversation step.

Return JSON only.
"""

    try:

        response = client.chat.completions.create(
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
            temperature=0,
            response_format={
                "type": "json_object"
            }
        )

        content = response.choices[0].message.content

        print(f"GROQ RAW RESPONSE: {content}")

        result = json.loads(content)

        return result

    except Exception as error:

        print(f"GROQ ERROR TYPE: {type(error).__name__}")
        print(f"GROQ ERROR: {error}")

        return {
            "intent": "UNKNOWN",
            "value": "",
            "confidence": 0
        }