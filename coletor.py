import random

from cache import (
    precisa_coletar,
    registrar_coleta
)

from config import MAX_COLETAS



# ==================================================
# COLETOR PRINCIPAL
# ==================================================

def coletar_produtos(
    sheet,
    produtos,
    colunas
):


    print(
        "=== INICIANDO COLETOR ==="
    )


    # Evita padrão fixo de coleta
    random.shuffle(produtos)


    coletados = 0



    for linha, produto in enumerate(
        produtos,
        start=2
    ):


        # Limite de consultas
        if coletados >= MAX_COLETAS:

            print(
                "Limite de coleta atingido."
            )

            break



        try:

            ultima_coleta = produto.get(
                "ULTIMA_COLETA_API",
                ""
            )


            intervalo = produto.get(
                "INTERVALO_COLETA_API",
                ""
            )



            # ==================================
            # CACHE
            # ==================================

            if not precisa_coletar(
                ultima_coleta,
                intervalo
            ):

                continue



            print(
                f"Produto liberado para coleta: linha {linha}"
            )



            # ==================================
            # AQUI O AMAPULSE SERÁ ATUALIZADO
            # PELA PLANILHA
            # ==================================

            atualizar_formula_amapulse(
                sheet,
                linha
            )



            # ==================================
            # REGISTRA CONSULTA
            # ==================================

            registrar_coleta(
                sheet,
                linha,
                colunas["ultima_coleta_api"],
                colunas["intervalo_api"]
            )


            coletados += 1



        except Exception as erro:


            print(
                f"[ERRO] Linha {linha}: {erro}"
            )



    print(
        f"=== FINALIZADO | {coletados} produtos consultados ==="
    )



# ==================================================
# FORÇA RECÁLCULO DAS FÓRMULAS
# ==================================================

def atualizar_formula_amapulse(
    sheet,
    linha
):

    """
    Força o Google Sheets a recalcular
    as fórmulas Amapulse.

    Mantém as fórmulas intactas.
    """

    valores = sheet.row_values(linha)


    sheet.update(
        f"A{linha}:Z{linha}",
        [valores]
    )



# ==================================================
# TESTE
# ==================================================

if __name__ == "__main__":

    print(
        "Coletor pronto."
    )
