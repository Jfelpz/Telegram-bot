from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def home():
    return "OAuth Mercado Livre online"


@app.route("/callback")
def callback():

    code = request.args.get("code")
    state = request.args.get("state")

    print("=" * 60)
    print("CALLBACK MERCADO LIVRE")
    print("CODE:", code)
    print("STATE:", state)
    print("=" * 60)

    if not code:
        return "Nenhum código recebido"

    return f"""
    <h2>Autorização Mercado Livre concluída</h2>

    <p>Copie este CODE:</p>

    <textarea rows="5" cols="80">{code}</textarea>
    """


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080
    )
