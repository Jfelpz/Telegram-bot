from sheets import (
    carregar_agulha,
    banco_sheet,
    obter_colunas,
    atualizar_celula
)


# ==========================================================
# SINCRONIZA AGULHA -> BANCO_DADOS
# ==========================================================

def sincronizar():

    print("=" * 60)
    print("SINCRONIZANDO AGULHA")
    print("=" * 60)

    agulha = carregar_agulha()

    if not agulha:

        print("AGULHA vazia.")

        return

    colunas = obter_colunas(banco_sheet)

    atualizados = 0

    for produto in agulha:

        row_banco = produto.get("ROW_BANCO")

        if not row_banco:
            continue

        try:
            row_banco = int(row_banco)
        except:
            continue

        preco = str(produto.get("PREÇO", "")).strip()
        preco_antigo = str(produto.get("PREÇO_ANTIGO", "")).strip()
        desconto = str(produto.get("DESCONTO", "")).strip()
        estoque = str(produto.get("ESTOQUE", "")).strip()
        ultima = str(produto.get("ULTIMA_ATUALIZAÇÃO", "")).strip()

        # -------------------------------------------------
        # Atualiza informações coletadas
        # -------------------------------------------------

        atualizar_celula(
            banco_sheet,
            row_banco,
            colunas["PREÇO"],
            preco
        )

        atualizar_celula(
            banco_sheet,
            row_banco,
            colunas["PREÇO_ANTIGO"],
            preco_antigo
        )

        atualizar_celula(
            banco_sheet,
            row_banco,
            colunas["DESCONTO"],
            desconto
        )

        atualizar_celula(
            banco_sheet,
            row_banco,
            colunas["ESTOQUE"],
            estoque
        )

        atualizar_celula(
            banco_sheet,
            row_banco,
            colunas["ULTIMA_ATUALIZAÇÃO"],
            ultima
        )

        # -------------------------------------------------
        # Define STATUS
        # -------------------------------------------------

        if estoque.upper() == "EM ESTOQUE":

            atualizar_celula(
                banco_sheet,
                row_banco,
                colunas["STATUS"],
                "PRONTO"
            )

        else:

            atualizar_celula(
                banco_sheet,
                row_banco,
                colunas["STATUS"],
                "PENDENTE"
            )

        atualizados += 1

    print()

    print(f"{atualizados} produto(s) sincronizados.")

    print("=" * 60)


# ==========================================================
# TESTE
# ==========================================================

if __name__ == "__main__":

    sincronizar()
