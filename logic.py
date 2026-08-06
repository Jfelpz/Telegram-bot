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
from mensagem import montar_mensagem


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
# PROCESSAMENTO
# =====================================================

def processar(dados_atualizados):

    print("=" * 60)
    print("INICIANDO PUBLICAÇÃO")
    print("=" * 60)

    config = carregar_config()

    print("\nCONFIGURAÇÕES")
    print("BOT_ATIVO:", config.get("BOT_ATIVO"))
    print("DESCONTO_MINIMO:", config.get("DESCONTO_MINIMO"))
    print("HORA_INICIO:", config.get("HORA_INICIO"))
    print("HORA_FIM:", config.get("HORA_FIM"))

    if not config.get("BOT_ATIVO", True):

        print("\nBOT DESLIGADO")
        return

    if not dentro_do_horario(config):

        print("\nFORA DO HORÁRIO")
        return

    desconto_minimo = float(
        config.get("DESCONTO_MINIMO", 0)
    )

    produtos = carregar_banco()

    print(f"\nProdutos encontrados: {len(produtos)}")

    colunas = obter_colunas(banco_sheet)

    for linha, produto in enumerate(produtos, start=2):

        print("\n" + "=" * 60)
        print(f"LINHA {linha}")

        print("Produto :", produto.get("PRODUTO"))
        print("Status  :", produto.get("STATUS"))
        print("Estoque :", produto.get("ESTOQUE"))
        print("Desconto:", produto.get("DESCONTO"))
        print("Ativo   :", produto.get("ATIVO"))
        print("Link    :", produto.get("LINK_AFILIADO"))

        # ==========================================
        # Dados completos vindos do coletor
        # ==========================================

        dados = dados_atualizados.get(linha)

        if dados is None:

            print("IGNORADO -> Produto não foi atualizado nesta execução.")

            continue

        # ==========================================
        # STATUS
        # ==========================================

        status = str(
            produto.get("STATUS", "")
        ).strip().upper()

        if status != "PENDENTE":

            print(f"IGNORADO -> STATUS = {status}")

            continue

        # ==========================================
        # ATIVO
        # ==========================================

        ativo = str(
            produto.get("ATIVO", "")
        ).strip().upper()

        if ativo not in (
            "TRUE",
            "VERDADEIRO",
            "SIM",
            "1"
        ):

            print("IGNORADO -> PRODUTO INATIVO")

            continue

        # ==========================================
        # ESTOQUE
        # ==========================================

        if not dados.get("estoque"):

            print("IGNORADO -> SEM ESTOQUE")

            continue

        # ==========================================
        # DESCONTO
        # ==========================================

        desconto = float(
            dados.get("desconto", 0)
        )

        if desconto < desconto_minimo:

            print(
                f"IGNORADO -> DESCONTO ({desconto:.2f}%) MENOR QUE ({desconto_minimo:.2f}%)"
            )

            continue

        # ==========================================
        # LINK
        # ==========================================
        
        link = str(
            produto.get("LINK_AFILIADO", "")
        ).strip()
        
        if not link.startswith("http"):
        
            print("IGNORADO -> LINK INVÁLIDO")
        
            continue
        
        # Sempre utiliza o link de afiliado
        dados["url"] = link

        # ==========================================
        # MONTA MENSAGEM
        # ==========================================

        mensagem = montar_mensagem(
            produto,
            dados
        )

        texto = mensagem["texto"]

        imagem = mensagem["imagem"]

        print()
        print("TODOS OS FILTROS PASSARAM")
        print("ENVIANDO PARA O TELEGRAM...")

        resposta = enviar(
            texto,
            imagem
        )

        print("Status Telegram:", resposta.status_code)

        if resposta.status_code != 200:

            print("ERRO AO ENVIAR")
            print(resposta.text)

            atualizar_celula(
                banco_sheet,
                linha,
                colunas["STATUS"],
                "ERRO"
            )

            continue

        agora = datetime.now(FUSO).strftime(
            "%d/%m/%Y %H:%M"
        )

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
            agora
        )

        atualizar_celula(
            banco_sheet,
            linha,
            colunas["ULTIMO_DESCONTO_ENVIADO"],
            round(desconto, 2)
        )

        print()
        print("PRODUTO ENVIADO COM SUCESSO")
        print(f"Data da postagem........: {agora}")
        print(f"Último desconto enviado.: {desconto:.2f}%")
        print("Status..................: ENVIADO")

        # Apenas um envio por execução
        return

    print()
    print("NENHUM PRODUTO ENCONTRADO PARA POSTAGEM")


# =====================================================
# TESTE
# =====================================================

if __name__ == "__main__":

    processar({})
