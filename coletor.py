import random

from datetime import datetime
from zoneinfo import ZoneInfo

from cache import precisa_coletar, registrar_coleta
from config import MAX_COLETAS


FUSO = ZoneInfo("America/Fortaleza")


# ==================================================
# AMAPULSE FUTURO
# ==================================================

def atualizar_produto(produto):
    """
    Futuramente será substituído pelo Amapulse.
    Retorna o preço encontrado na API.
    """

    try:
        preco_atual = float(
            produto.get("PREÇO", 100)
        )

    except:
        preco_atual = 100


    # simulação
    novo_preco = preco_atual - random.randint(1, 20)


    return round(novo_preco, 2)



# ==================================================
# VERIFICA SE PREÇO MUDOU
# ==================================================

def preco_alterou(preco_antigo, preco_novo):

    try:
        antigo = float(preco_antigo)
        novo = float(preco_novo)

        return antigo != novo

    except:
        return True



# ==================================================
# DATA DA ALTERAÇÃO DE PREÇO
# ==================================================

def data_atualizacao():

    return datetime.now(
        FUSO
    ).strftime(
        "%d/%m/%Y %H:%M"
    )



# ==================================================
# COLETOR PRINCIPAL
# ==================================================

def coletar_produtos(sheet, produtos, colunas):


    print("=== INICIANDO COLETOR ===")


    random.shuffle(produtos)


    coletados = 0


    for linha, produto in enumerate(produtos, start=2):


        if coletados >= MAX_COLETAS:

            print(
                "Limite de coletas atingido."
            )

            break



        try:

            ultima_coleta_api = produto.get(
                "ULTIMA_COLETA_API",
                ""
            )


            intervalo_api = produto.get(
                "INTERVALO_COLETA_API",
                ""
            )



            # ===============================
            # CACHE
            # ===============================

            if not precisa_coletar(
                ultima_coleta_api,
                intervalo_api
            ):

                continue



            print(
                f"Consultando produto linha {linha}"
            )



            # ===============================
            # CONSULTA API
            # ===============================

            novo_preco = atualizar_produto(
                produto
            )



            preco_antigo = produto.get(
                "PREÇO",
                ""
            )



            # ===============================
            # PREÇO MUDOU?
            # ===============================

            if preco_alterou(
                preco_antigo,
                novo_preco
            ):


                print(
                    "Preço alterado!"
                )


                # guarda preço antigo

                sheet.update_cell(
                    linha,
                    colunas["preco_antigo"],
                    preco_antigo
                )


                # atualiza preço

                sheet.update_cell(
                    linha,
                    colunas["preco"],
                    novo_preco
                )


                # registra data mudança

                sheet.update_cell(
                    linha,
                    colunas["ultima_atualizacao"],
                    data_atualizacao()
                )



            # ===============================
            # SEMPRE REGISTRA CONSULTA API
            # ===============================

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
        f"=== FINALIZADO | {coletados} consultados ==="
    )
