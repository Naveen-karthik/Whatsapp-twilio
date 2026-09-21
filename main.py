from fastapi import FastAPI
from route.whatsapp import router as whatsapp_router

app = FastAPI(
    title="Hospital WhatsApp Chatbot",
    version="1.0.0"
)

app.include_router(whatsapp_router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "Hospital WhatsApp Chatbot"
    }