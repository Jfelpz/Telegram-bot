import os
import requests

CLIENT_ID = os.getenv("ML_CLIENT_ID")
CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET")

CODE = "TG-6a6f6778c410a80001c0c6ee-1127744049"

REDIRECT_URI = "https://telegram-bot-jfelps.onrender.com/callback"

url = "https://api.mercadolibre.com/oauth/token"

payload = {
    "grant_type": "authorization_code",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "code": CODE,
    "redirect_uri": REDIRECT_URI
}

response = requests.post(url, data=payload)

print("Status:", response.status_code)
print(response.text)