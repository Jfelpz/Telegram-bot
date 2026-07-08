from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import random

from config import (
    COLETA_MIN_MINUTOS,
    COLETA_MAX_MINUTOS
)


FUSO = ZoneInfo("America/Fortaleza")


# ==================================================
# GERA INTERVALO INDIVIDUAL POR PRODUTO
# ==================================================

def gerar_intervalo():
    """
    Cria um intervalo aleatório para a próxima coleta.
    """

    return random.randint(
        COLETA_MIN_MINUTOS,
        COLETA_MAX_MINUTOS
    )


# ==================================================
# VERIFICA SE PRECISA CONSULTAR API
# ==================================================

def precisa_coletar(ultima_coleta_api, intervalo_api):
    """
    Decide se o produto pode ser consultado novamente.
    """

    if not ultima_coleta_api:
        return True

    try:
        ultima = datetime.strptime(
            ultima_coleta_api,
            "%d/%m/%Y %H:%M"
        ).replace(
            tzinfo=FUSO
        )

        intervalo = int(intervalo_api)

    except Exception:
        return True


    proxima_coleta = ultima + timedelta(
        minutes=intervalo
    )


    return datetime.now(FUSO) >= proxima_coleta



# ==================================================
# REGISTRA CONSULTA DA API
# ==================================================

def registrar_coleta(
    sheet,
    row_number,
    col_ultima_coleta_api,
    col_intervalo_api
):

    agora = datetime.now(FUSO).strftime(
        "%d/%m/%Y %H:%M"
    )

    novo_intervalo = gerar_intervalo()


    sheet.update_cell(
        row_number,
        col_ultima_coleta_api,
        agora
    )


    sheet.update_cell(
        row_number,
        col_intervalo_api,
        novo_intervalo
    )
