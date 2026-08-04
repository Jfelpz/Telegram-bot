import json
import requests
from pathlib import Path

from config import ML_CLIENT_ID, ML_CLIENT_SECRET

PKCE_FILE = Path("pkce.json")

if not PKCE_FILE.exists():
    raise FileNotFoundError(
        "Arquivo pkce.json não encontrado. Execute primeiro autenticar_ml.py."
    )

with open(PKCE_FILE, "r", encoding="utf-8") as f:
    pkce = json.load(f)

code = input("Cole aqui o CODE recebido: ").strip()

payload = {
    "grant_type": "authorization_code",
    "client_id": ML_CLIENT_ID,
    "client_secret": ML_CLIENT_SECRET,
    "code": code,
    "redirect_uri": "https://telegram-bot-ml-oauth.onrender.com/callback",
    "code_verifier": pkce["code_verifier"],
}

print("\nSolicitando tokens...\n")

r = requests.post(
    "https://api.mercadolibre.com/oauth/token",
    data=payload,
    timeout=30,
)

print("Status:", r.status_code)

try:
    resposta = r.json()
    print(json.dumps(resposta, indent=4, ensure_ascii=False))
except Exception:
    print(r.text)

if r.status_code == 200:
    with open("ml_tokens.json", "w", encoding="utf-8") as f:
        json.dump(resposta, f, indent=4, ensure_ascii=False)

    print("\n✅ Tokens salvos em ml_tokens.json")
else:
    print("\n❌ Não foi possível gerar os tokens.")
