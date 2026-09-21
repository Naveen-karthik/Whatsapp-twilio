from fastapi import APIRouter, Request
from fastapi.responses import Response

from service.conversation import handle_message

router = APIRouter()


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):

    form = await request.form()

    from_number = form.get("From")
    body = form.get("Body", "").strip()

    # WhatsApp button/list information
    button_text = form.get("ButtonText")
    button_payload = form.get("ButtonPayload")

    user_input = (
        button_payload
        or button_text
        or body
    )

    twiml_response = handle_message(
        phone_number=from_number,
        user_input=user_input
    )

    return Response(
        content=twiml_response,
        media_type="application/xml"
    )