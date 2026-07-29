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

💸 <s>R$ {preco_antigo}</s>

💰 <b>R$ {preco}</b>

🏷 {desconto}% OFF

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

        print("Fora do horário permitido.")
        return

    desconto_minimo = float(
        config.get("DESCONTO_MINIMO", 0)
    )

    produtos = carregar_banco()

    colunas = obter_colunas(banco_sheet)

    # começa na linha 2 porque a linha 1 é o cabeçalho
    for linha, produto in enumerate(produtos, start=2):

        status = str(
            produto.get("STATUS", "")
        ).strip().upper()

        if status != "PRONTO":
            continue

        estoque = str(
            produto.get("ESTOQUE", "")
        ).strip().upper()

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

        link = str(
            produto.get("LINK_AFILIADO", "")
        ).strip()

        if not link.startswith("http"):
            print("Link inválido.")
            continue

        mensagem = montar_mensagem(produto)

        print(f"Enviando: {produto.get('PRODUTO')}")

        resposta = enviar(mensagem)

        if resposta.status_code != 200:

            print("Erro ao enviar para o Telegram.")
            print(resposta.text)
            continue

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

        # envia apenas um produto por execução
        return

    print("Nenhum produto encontrado para postagem.")


# =====================================================
# TESTE
# =====================================================

if __name__ == "__main__":
    processar()
