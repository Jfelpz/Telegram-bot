from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def home():
    return "Servidor OAuth Mercado Livre ativo"


@app.route("/callback")
def callback():

    code = request.args.get("code")
    state = request.args.get("state")

    print("=" * 50)
    print("CALLBACK MERCADO LIVRE")
    print("CODE:", code)
    print("STATE:", state)
    print("=" * 50)

    if code:
        return f"""
        <h2>Autorização recebida!</h2>
        <p>CODE:</p>
        <textarea>{code}</textarea>
        """

    return "Nenhum código recebido"


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080
    )
