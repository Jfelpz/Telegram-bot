from sheets import (
    carregar_agulha,
    banco_sheet,
    obter_colunas
)


# ==================================================
# SINCRONIZA AGULHA -> BANCO_DADOS
# ==================================================

def sincronizar():

    print("=" * 60)
    print("SINCRONIZANDO AGULHA")
    print("=" * 60)

    agulha = carregar_agulha()

    if not agulha:

        print("AGULHA vazia.")

        return

    colunas = obter_colunas(
        banco_sheet
    )

    atualizados = 0

    for produto in agulha:

        try:

            row = int(
                produto["ROW_BANCO"]
            )

        except:

            continue

        try:

            banco_sheet.update_cell(
                row,
                colunas["PREÇO"],
                produto.get(
                    "PREÇO",
                    ""
                )
            )

            banco_sheet.update_cell(
                row,
                colunas["PREÇO_ANTIGO"],
                produto.get(
                    "PREÇO_ANTIGO",
                    ""
                )
            )

            banco_sheet.update_cell(
                row,
                colunas["DESCONTO"],
                produto.get(
                    "DESCONTO",
                    ""
                )
            )

            banco_sheet.update_cell(
                row,
                colunas["ESTOQUE"],
                produto.get(
                    "ESTOQUE",
                    ""
                )
            )

            banco_sheet.update_cell(
                row,
                colunas["ULTIMA_ATUALIZAÇÃO"],
                produto.get(
                    "ULTIMA_ATUALIZAÇÃO",
                    ""
                )
            )

            atualizados += 1

        except Exception as erro:

            print(
                f"Erro linha {row}: {erro}"
            )

    print()

    print(
        f"{atualizados} produtos sincronizados."
    )

    print("=" * 60)


# ==================================================
# TESTE
# ==================================================

if __name__ == "__main__":

    sincronizar()
