from celery import shared_task
import requests

@shared_task
def send_telegram_message(chat_id, message):
    token = "8757257839:AAGVoHlQdKrFfb_xQnARHZwtFHdGbw1OfE8"

    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": message,
        },
        timeout=15,
    )
    response.raise_for_status()

    return "Xabar yuborildi"