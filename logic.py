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
# HORÁRIO DE FUNCIONAMENTO
# =====================================================

def dentro_do_horario(config):

    try:

        inicio = datetime.strptime(
            config.get("HORA_INICIO", "00:00"),
            "%H:%M"
        ).time()

        fim = datetime.strptime(
            config.get("HORA_FIM", "23:59"),
            "%H:%M"
        ).time()

        agora = datetime.now(FUSO).time()

        return inicio <= agora <= fim

    except:

        return True


# =====================================================
# MENSAGEM TELEGRAM
# =====================================================

def montar_mensagem(produto):

    nome = produto.get("PRODUTO", "")

    preco = produto.get("PREÇO", "")

    preco_antigo = produto.get("PREÇO_ANTIGO", "")

    desconto = produto.get("DESCONTO", "")

    loja = produto.get("LOJA", "")

    link = produto.get("LINK_AFILIADO", "")

    mensagem = f"""
🔥 <b>{nome}</b>

🏪 Loja: {loja}

💰 De: R$ {preco_antigo}

💵 Por: <b>R$ {preco}</b>

🏷 Desconto: {desconto}%

🛒 Comprar:
{link}
"""

    return mensagem.strip()


# =====================================================
# PROCESSAMENTO
# =====================================================

def processar():

    print("=" * 60)
    print("INICIANDO PUBLICAÇÃO")
    print("=" * 60)

    config = carregar_config()

    if not config.get("BOT_ATIVO", True):

        print("Bot desligado.")

        return

    if not dentro_do_horario(config):

        print("Fora do horário.")

        return

    desconto_minimo = float(
        config.get("DESCONTO_MINIMO", 0)
    )

    produtos = carregar_banco()

    colunas = obter_colunas(banco_sheet)

    for produto in produtos:

        status = str(
            produto.get("STATUS", "")
        ).upper().strip()

        if status != "PRONTO":
            continue

        estoque = str(
            produto.get("ESTOQUE", "")
        ).upper().strip()

        if estoque not in (
            "TRUE",
            "SIM",
            "EM ESTOQUE",
            "DISPONIVEL",
            "DISPONÍVEL",
            "1"
        ):
            continue

        try:

            desconto = float(
                str(
                    produto.get("DESCONTO", "0")
                ).replace("%", "").replace(",", ".")
            )

        except:

            desconto = 0

        if desconto < desconto_minimo:

            continue

        mensagem = montar_mensagem(produto)

        print()

        print("Enviando:")

        print(produto["PRODUTO"])

        enviar(mensagem)

        linha = produto["ROW_NUMBER"]

        atualizar_celula(
            banco_sheet,
            linha,
            colunas["STATUS"],
            "ENVIADO"
        )

        atualizar_celula(
            banco_sheet,
            linha,
            colunas["DATA_POSTAGEM"],
            datetime.now(FUSO).strftime("%d/%m/%Y %H:%M")
        )

        print("Produto enviado com sucesso.")

        return

    print("Nenhum produto disponível para postagem.")


# =====================================================
# TESTE
# =====================================================

if __name__ == "__main__":

    processar()
