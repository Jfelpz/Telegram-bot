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


def atualizar_produtos():

    print("=" * 60)
    print("ATUALIZANDO PRODUTOS")
    print("=" * 60)

    produtos = carregar_banco()

    colunas = obter_colunas(banco_sheet)

    atualizados = 0
    erros = 0

    for indice, produto in enumerate(produtos, start=2):

        url = str(produto.get("URL_ORIGEM", "")).strip()

        if not url:
            continue

        print()
        print(f"[{indice}] {url}")

        dados = coletar_produto(url)

        if dados.get("erro"):

            print("Erro:", dados["mensagem"])
            erros += 1
            continue

        atualizar_linha(
            banco_sheet,
            indice,
            {
                colunas["PREÇO"]: dados["preco"],
                colunas["PREÇO_PIX"]: dados["preco_pix"],
                colunas["DESCONTO"]: dados["desconto"],
                colunas["ESTOQUE"]: dados["estoque"],
                colunas["MARCA"]: dados["marca"],
                colunas["CATEGORIA"]: dados["categoria"],
                colunas["SUBCATEGORIA"]: dados["subcategoria"],
                colunas["IMAGEM"]: dados["imagem"],
                colunas["AVALIAÇÃO"]: dados["avaliacao"],
                colunas["TOTAL_AVALIAÇÕES"]: dados["total_avaliacoes"],
                colunas["ULTIMA_ATUALIZAÇÃO"]:
                    datetime.now(FUSO).strftime("%d/%m/%Y %H:%M")
            }
        )

        atualizados += 1

        print("OK")

    print()
    print("=" * 60)
    print("FINALIZADO")
    print("=" * 60)
    print(f"Atualizados: {atualizados}")
    print(f"Erros: {erros}")


if __name__ == "__main__":

    atualizar_produtos()
