from datetime import datetime
from zoneinfo import ZoneInfo

from coletores.base import coletar_produto

from sheets import (
    carregar_banco,
    banco_sheet,
    obter_colunas,
    atualizar_linha
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

    colunas = obter_colunas(banco_sheet)

    atualizados = 0
    erros = 0

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

        # =====================================================
        # DESCONTO NOVO
        # =====================================================

        desconto_novo = round(
            float(dados.get("desconto", 0)),
            2
        )

        # =====================================================
        # ÚLTIMO DESCONTO ENVIADO
        # =====================================================

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

        # =====================================================
        # REPOSTAGEM
        # =====================================================

        if status == "ENVIADO":

            if desconto_novo >= (
                ultimo_desconto + AUMENTO_MINIMO_REPOSTAGEM
            ):

                novo_status = "PENDENTE"

                print(
                    f"↻ Repostagem liberada "
                    f"({ultimo_desconto:.2f}% -> {desconto_novo:.2f}%)"
                )

        elif status == "PAUSADO":

            novo_status = "PAUSADO"

        # =====================================================
        # SEM ESTOQUE
        # =====================================================

        if not dados.get("estoque"):

            novo_status = "SEM_ESTOQUE"

        # =====================================================
        # ATUALIZA PLANILHA
        # =====================================================

        atualizar_linha(

            banco_sheet,

            linha,

            {

                colunas["LOJA"]:
                    dados.get("loja", ""),

                colunas["PRODUTO"]:
                    dados.get("produto", ""),

                colunas["CATEGORIA"]:
                    dados.get("categoria", ""),

                colunas["PREÇO"]:
                    round(
                        float(
                            dados.get("preco", 0)
                        ),
                        2
                    ),

                colunas["PREÇO_ANTIGO"]:
                    round(
                        float(
                            dados.get("preco_antigo", 0)
                        ),
                        2
                    ),

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
                    )

            }

        )

        atualizados += 1

        print("✔ Produto atualizado")
        print("-" * 50)
        print(f"Produto................: {dados.get('produto')}")
        print(f"Preço antigo...........: R$ {dados.get('preco_antigo'):.2f}")
        print(f"Preço atual............: R$ {dados.get('preco'):.2f}")
        print(f"Preço PIX..............: R$ {dados.get('preco_pix'):.2f}")
        print(f"Desconto atual.........: {desconto_novo:.2f}%")
        print(f"Último enviado.........: {ultimo_desconto:.2f}%")
        print(f"Estoque................: {'SIM' if dados.get('estoque') else 'NÃO'}")
        print(f"Status.................: {novo_status}")
        print("-" * 50)

    print()
    print("=" * 60)
    print("FINALIZADO")
    print("=" * 60)
    print(f"Produtos atualizados: {atualizados}")
    print(f"Erros: {erros}")


# =====================================================
# EXECUÇÃO
# =====================================================

if __name__ == "__main__":

    atualizar_produtos()
