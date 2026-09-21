from typing import Dict

from twilio.twiml.messaging_response import MessagingResponse


# Temporary in-memory storage.
# Later we will replace this with Redis/MongoDB.
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

    user_input_lower = user_input.lower().strip()

    # ---------------------------
    # WELCOME
    # ---------------------------

    if step == "WELCOME":

        if user_input_lower in [
            "yes",
            "yes lets start",
            "start"
        ]:

            session["step"] = "PATIENT_NAME"

            return twiml_text(
                "Great! 👋\n\n"
                "May I have the patient's full name, please?"
            )

        if user_input_lower in [
            "working hours",
            "hours"
        ]:

            return twiml_text(
                "🕘 Our working hours are:\n\n"
                "Monday - Saturday\n"
                "9:00 AM - 6:00 PM"
            )

        if user_input_lower in [
            "exit",
            "cancel"
        ]:

            session["step"] = "WELCOME"

            return twiml_text(
                "Okay 👍\n"
                "If you need an appointment later, just message us."
            )

        return twiml_text(
            "Welcome! 👋\n\n"
            "I can help you book an appointment quickly.\n\n"
            "Shall we get started?"
        )

    # ---------------------------
    # PATIENT NAME
    # ---------------------------

    if step == "PATIENT_NAME":

        session["patient_name"] = user_input

        session["step"] = "DOCTOR"

        return twiml_text(
            f"Thanks, {user_input}! 😊\n\n"
            "Please choose a doctor:\n\n"
            "1. Dr. Shalini - Dermatologist\n"
            "2. Dr. Raj - Pediatrician\n"
            "3. Dr. Kumar - Dental"
        )

    # ---------------------------
    # DOCTOR
    # ---------------------------

    if step == "DOCTOR":

        doctor = None

        if "shalini" in user_input_lower:
            doctor = DOCTORS["doctor_shalini"]

        elif "raj" in user_input_lower:
            doctor = DOCTORS["doctor_raj"]

        elif "kumar" in user_input_lower:
            doctor = DOCTORS["doctor_kumar"]

        if not doctor:

            return twiml_text(
                "Please select one of the available doctors."
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

    # ---------------------------
    # APPOINTMENT TYPE
    # ---------------------------

    if step == "APPOINTMENT_TYPE":

        appointment_types = {
            "initial consultation": "Initial Consultation",
            "follow up consultation": "Follow-up Consultation",
            "follow-up consultation": "Follow-up Consultation",
            "virtual meeting": "Virtual Meeting",
            "in person meeting": "In-person Meeting",
            "in-person meeting": "In-person Meeting"
        }

        appointment_type = appointment_types.get(
            user_input_lower
        )

        if not appointment_type:

            return twiml_text(
                "Please select a valid appointment type."
            )

        session["appointment_type"] = appointment_type

        session["step"] = "DATE"

        return twiml_text(
            "Which date would you prefer? 📅\n\n"
            "1. Today\n"
            "2. Tomorrow\n"
            "3. Later"
        )

    # ---------------------------
    # DATE
    # ---------------------------

    if step == "DATE":

        if "today" in user_input_lower:

            selected_date = "Today"

        elif "tomorrow" in user_input_lower:

            selected_date = "Tomorrow"

        elif "later" in user_input_lower:

            selected_date = "Later"

        else:

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

    # ---------------------------
    # TIME
    # ---------------------------

    if step == "TIME":

        valid_times = [
            "11:00 am",
            "12:00 pm",
            "2:00 pm",
            "3:00 pm",
            "5:00 pm"
        ]

        if user_input_lower not in valid_times:

            return twiml_text(
                "Please select one of the available time slots."
            )

        session["time"] = user_input

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
            "If you need to reschedule, please reply "
            "with 'reschedule'."
        )

    # ---------------------------
    # CONFIRMED
    # ---------------------------

    if step == "CONFIRMED":

        if "reschedule" in user_input_lower:

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
            "Reply 'reschedule' if you want to change it."
        )

    return twiml_text(
        "Sorry, something went wrong. Please type 'start' "
        "to begin again."
    )