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
# ATUALIZADOR DE PRODUTOS
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

        atualizar_linha(

            banco_sheet,

            linha,

            {

                # ==========================================
                # PRODUTO
                # ==========================================

                colunas["LOJA"]:
                    dados.get("loja", ""),

                colunas["PRODUTO"]:
                    dados.get("produto", ""),

                colunas["CATEGORIA"]:
                    dados.get("categoria", ""),

                # ==========================================
                # PREÇOS
                # ==========================================

                colunas["PREÇO"]:
                    round(float(dados.get("preco", 0)), 2),

                colunas["PREÇO_ANTIGO"]:
                    round(float(dados.get("preco_antigo", 0)), 2),

                colunas["DESCONTO"]:
                    round(float(dados.get("desconto", 0)), 2),

                # ==========================================
                # ESTOQUE
                # ==========================================

                colunas["ESTOQUE"]:
                    "EM ESTOQUE"
                    if dados.get("estoque")
                    else "SEM ESTOQUE",

                # ==========================================
                # DATA
                # ==========================================

                colunas["ULTIMA_ATUALIZAÇÃO"]:
                    datetime.now(FUSO).strftime(
                        "%d/%m/%Y %H:%M"
                    )

            }

        )

        atualizados += 1

        print("✔ Produto atualizado")
        print("-" * 40)
        print(f"Produto       : {dados.get('produto')}")
        print(f"Preço antigo  : R$ {dados.get('preco_antigo'):.2f}")
        print(f"Preço atual   : R$ {dados.get('preco'):.2f}")
        print(f"Preço PIX     : R$ {dados.get('preco_pix'):.2f}")
        print(f"Desconto real : {dados.get('desconto'):.2f}%")
        print(f"Estoque       : {'SIM' if dados.get('estoque') else 'NÃO'}")
        print("-" * 40)

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
