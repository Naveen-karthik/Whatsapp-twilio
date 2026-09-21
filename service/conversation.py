from typing import Dict

from twilio.twiml.messaging_response import MessagingResponse

from llm.groq_client import understand_message


# Temporary in-memory storage.
# Later replace with Redis/MongoDB.
sessions: Dict[str, dict] = {}


DOCTORS = {
    "doctor_shalini": {
        "name": "Dr. Shalini",
        "specialization": "Dermatologist"
    },
    "doctor_raj": {
        "name": "Dr. Raj",
        "specialization": "Pediatrician"
    },
    "doctor_kumar": {
        "name": "Dr. Kumar",
        "specialization": "Dental"
    }
}


APPOINTMENT_TYPES = {
    "initial consultation": "Initial Consultation",
    "follow-up consultation": "Follow-up Consultation",
    "virtual meeting": "Virtual Meeting",
    "in-person meeting": "In-person Meeting"
}


DATES = {
    "today": "Today",
    "tomorrow": "Tomorrow",
    "later": "Later"
}


VALID_TIMES = {
    "11:00 AM",
    "12:00 PM",
    "2:00 PM",
    "3:00 PM",
    "5:00 PM"
}


def get_session(phone_number: str):

    if phone_number not in sessions:

        sessions[phone_number] = {
            "step": "WELCOME",
            "patient_name": None,
            "doctor": None,
            "appointment_type": None,
            "date": None,
            "time": None
        }

    return sessions[phone_number]


def twiml_text(message: str):

    response = MessagingResponse()

    response.message(message)

    return str(response)


def handle_message(phone_number: str, user_input: str):

    session = get_session(phone_number)

    step = session["step"]

    print("\n-------------------------------")
    print(f"PHONE: {phone_number}")
    print(f"STEP: {step}")
    print(f"USER: {user_input}")

    # Ask Mistral to understand the user.
    result = understand_message(
        user_input=user_input,
        current_step=step
    )

    intent = result.get("intent", "UNKNOWN")
    value = result.get("value", "")
    confidence = result.get("confidence", 0)

    print(f"LLM INTENT: {intent}")
    print(f"LLM VALUE: {value}")
    print(f"LLM CONFIDENCE: {confidence}")

    # -----------------------------------------
    # WELCOME
    # -----------------------------------------

    if step == "WELCOME":

        if intent == "WELCOME_START":

            session["step"] = "PATIENT_NAME"

            return twiml_text(
                "Great! 👋\n\n"
                "May I have the patient's full name, please?"
            )

        if intent == "WORKING_HOURS":

            return twiml_text(
                "🕘 Our working hours are:\n\n"
                "Monday - Saturday\n"
                "9:00 AM - 6:00 PM"
            )

        if intent == "EXIT":

            session["step"] = "WELCOME"

            return twiml_text(
                "Okay 👍\n"
                "If you need an appointment later, just message us."
            )

        return twiml_text(
            "Welcome! 👋\n\n"
            "I can help you book an appointment quickly.\n\n"
            "You can say:\n"
            "• Start booking\n"
            "• Working hours\n"
            "• Exit"
        )

    # -----------------------------------------
    # PATIENT NAME
    # -----------------------------------------

    if step == "PATIENT_NAME":

        if intent != "PATIENT_NAME" or not value:

            return twiml_text(
                "Please provide the patient's full name."
            )

        session["patient_name"] = value

        session["step"] = "DOCTOR"

        return twiml_text(
            f"Thanks, {value}! 😊\n\n"
            "Please choose a doctor:\n\n"
            "1. Dr. Shalini - Dermatologist\n"
            "2. Dr. Raj - Pediatrician\n"
            "3. Dr. Kumar - Dental"
        )

    # -----------------------------------------
    # DOCTOR
    # -----------------------------------------

    if step == "DOCTOR":

        if intent != "SELECT_DOCTOR":

            return twiml_text(
                "Please select one of our available doctors."
            )

        doctor = DOCTORS.get(value)

        if not doctor:

            return twiml_text(
                "I couldn't identify that doctor.\n\n"
                "Please choose Dr. Shalini, Dr. Raj, or Dr. Kumar."
            )

        session["doctor"] = doctor

        session["step"] = "APPOINTMENT_TYPE"

        return twiml_text(
            f"Doctor selected: {doctor['name']} "
            f"({doctor['specialization']}) ✅\n\n"
            "Please select the type of appointment:\n\n"
            "1. Initial Consultation\n"
            "2. Follow-up Consultation\n"
            "3. Virtual Meeting\n"
            "4. In-person Meeting"
        )

    # -----------------------------------------
    # APPOINTMENT TYPE
    # -----------------------------------------

    if step == "APPOINTMENT_TYPE":

        if intent != "SELECT_APPOINTMENT_TYPE":

            return twiml_text(
                "Please select a valid appointment type."
            )

        appointment_type = APPOINTMENT_TYPES.get(
            value.lower()
        )

        if not appointment_type:

            return twiml_text(
                "Please choose one of the available appointment types."
            )

        session["appointment_type"] = appointment_type

        session["step"] = "DATE"

        return twiml_text(
            "Which date would you prefer? 📅\n\n"
            "1. Today\n"
            "2. Tomorrow\n"
            "3. Later"
        )

    # -----------------------------------------
    # DATE
    # -----------------------------------------

    if step == "DATE":

        if intent != "SELECT_DATE":

            return twiml_text(
                "Please select Today, Tomorrow, or Later."
            )

        selected_date = DATES.get(
            value.lower()
        )

        if not selected_date:

            return twiml_text(
                "Please select Today, Tomorrow, or Later."
            )

        session["date"] = selected_date

        session["step"] = "TIME"

        return twiml_text(
            f"{selected_date} selected 📅\n\n"
            "Please select a time:\n\n"
            "11:00 AM\n"
            "12:00 PM\n"
            "2:00 PM\n"
            "3:00 PM\n"
            "5:00 PM"
        )

    # -----------------------------------------
    # TIME
    # -----------------------------------------

    if step == "TIME":

        if intent != "SELECT_TIME":

            return twiml_text(
                "Please select one of the available time slots:\n\n"
                "11:00 AM\n"
                "12:00 PM\n"
                "2:00 PM\n"
                "3:00 PM\n"
                "5:00 PM"
            )

        selected_time = value.strip().upper()

        if selected_time not in VALID_TIMES:

            return twiml_text(
                "Please select one of the available time slots."
            )

        session["time"] = selected_time

        session["step"] = "CONFIRMED"

        doctor = session["doctor"]

        return twiml_text(
            "✅ Appointment Confirmed!\n\n"
            f"Patient: {session['patient_name']}\n"
            f"Doctor: {doctor['name']}\n"
            f"Specialization: {doctor['specialization']}\n"
            f"Appointment: {session['appointment_type']}\n"
            f"Date: {session['date']}\n"
            f"Time: {session['time']}\n\n"
            f"Thank you! Your appointment is scheduled "
            f"for {session['date']} at {session['time']} "
            f"with {doctor['name']}.\n\n"
            "If you need to reschedule, just say "
            "'reschedule'."
        )

    # -----------------------------------------
    # CONFIRMED
    # -----------------------------------------

    if step == "CONFIRMED":

        if intent == "RESCHEDULE":

            session["step"] = "DATE"

            return twiml_text(
                "Sure! Let's reschedule your appointment. 📅\n\n"
                "Please select a new date:\n"
                "1. Today\n"
                "2. Tomorrow\n"
                "3. Later"
            )

        return twiml_text(
            "Your appointment is already scheduled. ✅\n\n"
            "You can say 'reschedule' if you want to "
            "change it."
        )

    return twiml_text(
        "Sorry, something went wrong. "
        "Please say 'start' to begin again."
    )
