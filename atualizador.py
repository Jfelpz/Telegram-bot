from datetime import datetime
from zoneinfo import ZoneInfo

from coletores.base import coletar_produto

from sheets import (
    carregar_banco,
    banco_sheet,
    obter_colunas,
    atualizar_linha,
    garantir_ids
)

FUSO = ZoneInfo("America/Fortaleza")

# =====================================================
# CONFIGURAÇÃO
# =====================================================

AUMENTO_MINIMO_REPOSTAGEM = 3.0

# =====================================================
# ATUALIZADOR
# =====================================================

def atualizar_produtos():

    print("=" * 60)
    print("ATUALIZANDO PRODUTOS")
    print("=" * 60)

    produtos = carregar_banco()

    print(f"Produtos encontrados na planilha: {len(produtos)}")

    colunas = obter_colunas(banco_sheet)

    ids_gerados = garantir_ids(produtos, colunas)

    if ids_gerados:
        print(f"IDs gerados nesta execução: {ids_gerados}")

    atualizados = 0
    erros = 0

    houve_repostagem = False

    # Guarda todos os produtos coletados
    dados_atualizados = {}

    print("Iniciando coleta...")

    for linha, produto in enumerate(produtos, start=2):

        url = str(
            produto.get("URL_ORIGEM", "")
        ).strip()

        if not url:
            continue

        print()
        print(f"[{linha}] Atualizando...")
        print(url)

        try:

            dados = coletar_produto(url)

        except Exception as erro:

            print("Erro:", erro)

            erros += 1
            continue

        if dados.get("erro"):

            print("Erro:", dados["mensagem"])

            erros += 1
            continue

        # Guarda os dados completos para o logic.py
        dados_atualizados[linha] = dados

        desconto_novo = round(
            float(dados.get("desconto") or 0),
            2
        )

        preco = round(
            float(dados.get("preco") or 0),
            2
        )

        preco_antigo = round(
            float(dados.get("preco_antigo") or 0),
            2
        )

        preco_pix = round(
            float(dados.get("preco_pix") or preco),
            2
        )

        try:

            ultimo_desconto = float(
                str(
                    produto.get(
                        "ULTIMO_DESCONTO_ENVIADO",
                        0
                    )
                ).replace(",", ".")
            )

        except:

            ultimo_desconto = 0.0

        status = str(
            produto.get(
                "STATUS",
                ""
            )
        ).strip().upper()

        novo_status = status

        # ================================================
        # REPOSTAGEM
        # ================================================

        if status == "ENVIADO":

            if desconto_novo >= (
                ultimo_desconto + AUMENTO_MINIMO_REPOSTAGEM
            ):

                novo_status = "PENDENTE"

                houve_repostagem = True

                print(
                    f"↻ Repostagem liberada "
                    f"({ultimo_desconto:.2f}% -> {desconto_novo:.2f}%)"
                )

        elif status == "PAUSADO":

            novo_status = "PAUSADO"

        elif status == "ERRO":

            novo_status = "PENDENTE"

        # ================================================
        # ESTOQUE
        # ================================================

        if dados.get("estoque"):

            if status == "SEM_ESTOQUE":

                novo_status = "PENDENTE"

                print("Produto voltou ao estoque.")

        else:

            novo_status = "SEM_ESTOQUE"
        # ================================================
        # ATUALIZA PLANILHA
        # ================================================

        atualizar_linha(

            banco_sheet,

            linha,

            {

                colunas["LOJA"]:
                    dados.get("loja", ""),

                colunas["PRODUTO"]:
                    dados.get("produto", ""),

                colunas["PREÇO"]:
                    preco,

                colunas["PREÇO_ANTIGO"]:
                    preco_antigo,

                colunas["DESCONTO"]:
                    desconto_novo,

                colunas["ESTOQUE"]:
                    "EM ESTOQUE"
                    if dados.get("estoque")
                    else "SEM ESTOQUE",

                colunas["STATUS"]:
                    novo_status,

                colunas["ULTIMA_ATUALIZAÇÃO"]:
                    datetime.now(FUSO).strftime(
                        "%d/%m/%Y %H:%M"
                    ),

                # ======================================
                # CAMPOS ATUALIZADOS PELO COLETOR
                # ======================================

                colunas["IMAGEM"]:
                    dados.get("imagem", ""),

                colunas["IDENTIFICADOR"]:
                    dados.get("identificador", "")

            }

        )

        atualizados += 1

        print("✔ Produto atualizado")
        print("-" * 50)
        print(f"Produto................: {dados.get('produto')}")
        print(f"Preço antigo...........: R$ {preco_antigo:.2f}")
        print(f"Preço atual............: R$ {preco:.2f}")
        print(f"Preço PIX..............: R$ {preco_pix:.2f}")
        print(f"Desconto atual.........: {desconto_novo:.2f}%")
        print(f"Último enviado.........: {ultimo_desconto:.2f}%")
        print(f"Estoque................: {'SIM' if dados.get('estoque') else 'NÃO'}")
        print(f"Status.................: {novo_status}")
        print(f"Imagem.................: {dados.get('imagem', '')}")
        print(f"Identificador..........: {dados.get('identificador', '')}")
        print("-" * 50)
        # =====================================================
    # FIM DA COLETA
    # =====================================================

    print()
    print("=" * 60)
    print("FINALIZADO")
    print("=" * 60)
    print(f"Produtos atualizados: {atualizados}")
    print(f"Erros: {erros}")

    # =====================================================
    # RETORNO PARA O BOT
    # =====================================================

    return {

        "houve_repostagem": houve_repostagem,

        "dados_atualizados": dados_atualizados

    }


# =====================================================
# EXECUÇÃO LOCAL (APENAS TESTE)
# =====================================================

if __name__ == "__main__":

    resultado = atualizar_produtos()

    print()
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)

    print(
        "Houve repostagem:",
        resultado["houve_repostagem"]
    )

    print(
        "Produtos coletados:",
        len(resultado["dados_atualizados"])
    )

    if resultado["dados_atualizados"]:

        print()

        print("Produtos retornados:")

        for linha, dados in resultado["dados_atualizados"].items():

            print(
                f"Linha {linha}"
            )

            print(
                f"Produto : {dados.get('produto')}"
            )

            print(
                f"Preço   : R$ {dados.get('preco', 0):.2f}"
            )

            print(
                f"Desconto: {dados.get('desconto', 0):.2f}%"
            )

            print(
                f"Estoque : {dados.get('estoque')}"
            )

            print("-" * 40)
