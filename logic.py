from datetime import datetime
from zoneinfo import ZoneInfo

from sheets import (
    carregar_banco,
    carregar_config,
    banco_sheet,
    obter_colunas,
    atualizar_celula
)

from telegram import enviar


FUSO = ZoneInfo("America/Fortaleza")


# =====================================================
# VERIFICA HORÁRIO DE FUNCIONAMENTO
# =====================================================

def dentro_do_horario(config):

    agora = datetime.now(FUSO).time()

    hora_inicio = datetime.strptime(
        config["HORA_INICIO"],
        "%H:%M"
    ).time()

    hora_fim = datetime.strptime(
        config["HORA_FIM"][:5],
        "%H:%M"
    ).time()

    return hora_inicio <= agora <= hora_fim


# =====================================================
# PROCESSAMENTO PRINCIPAL
# =====================================================

def processar():

    print("=" * 60)
    print("PROCESSANDO PUBLICAÇÕES")
    print("=" * 60)

    config = carregar_config()

    # -------------------------------------------------

    if not config.get("BOT_ATIVO", True):

        print("Bot desativado.")

        return

    # -------------------------------------------------

    if not dentro_do_horario(config):

        print("Fora do horário permitido.")

        return

    # -------------------------------------------------

    desconto_minimo = float(
        config.get(
            "DESCONTO_MINIMO",
            15
        )
    )

    produtos = carregar_banco()

    colunas = obter_colunas(
        banco_sheet
    )

    enviados = 0

    # -------------------------------------------------

    for produto in produtos:

        status = str(
            produto.get(
                "STATUS",
                ""
            )
        ).strip().upper()

        if status != "PRONTO":
            continue

        nome = str(
            produto.get(
                "PRODUTO",
                ""
            )
        ).strip()

        estoque = str(
            produto.get(
                "ESTOQUE",
                ""
            )
        ).strip().upper()

        if estoque != "EM ESTOQUE":

            print(
                f"Sem estoque: {nome}"
            )

            continue

        desconto = str(
            produto.get(
                "DESCONTO",
                ""
            )
        ).replace(
            "%",
            ""
        ).replace(
            ",",
            "."
        )

        try:

            desconto_float = float(
                desconto
            )

        except:

            desconto_float = 0

        if desconto_float < desconto_minimo:

            print(
                f"Desconto insuficiente: {nome}"
            )

            continue

        link = str(
            produto.get(
                "LINK_AFILIADO",
                ""
            )
        ).strip()

        if not link.startswith("http"):

            print(
                f"Link inválido: {nome}"
            )

            continue

        preco = produto.get(
            "PREÇO",
            ""
        )

        preco_antigo = produto.get(
            "PREÇO_ANTIGO",
            ""
        )

        categoria = produto.get(
            "CATEGORIA",
            ""
        )

        loja = produto.get(
            "LOJA",
            ""
        )

        # -------------------------------------------------
# Monta mensagem
# -------------------------------------------------

mensagem = montar_mensagem(produto)

print(f"Enviando {nome}")

try:

    enviar(mensagem)

except Exception as erro:

    print(erro)

    continue

row = int(produto["ROW_NUMBER"])

atualizar_celula(

    banco_sheet,

    row,

    colunas["STATUS"],

    "ENVIADO"

)

atualizar_celula(

    banco_sheet,

    row,

    colunas["DATA_POSTAGEM"],

    datetime.now(FUSO).strftime(
        "%d/%m/%Y %H:%M"
    )

)

# =====================================================
# TESTE
# =====================================================

if __name__ == "__main__":

    processar()
