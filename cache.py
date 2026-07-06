from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import random


FUSO = ZoneInfo("America/Fortaleza")

# Intervalo mínimo e máximo entre coletas (em minutos)
MIN_INTERVALO = 60
MAX_INTERVALO = 90


def precisa_coletar(ultima_coleta, intervalo):
    """
    Retorna True se o produto precisa ser atualizado.
    """

    if not ultima_coleta:
        return True

    try:
        ultima = datetime.strptime(
            ultima_coleta,
            "%d/%m/%Y %H:%M"
        ).replace(tzinfo=FUSO)

        minutos = int(intervalo)

    except Exception:
        return True

    proxima = ultima + timedelta(minutes=minutos)

    return datetime.now(FUSO) >= proxima


def gerar_intervalo():
    """
    Gera um intervalo aleatório entre 60 e 90 minutos.
    """

    return random.randint(
        MIN_INTERVALO,
        MAX_INTERVALO
    )


def registrar_coleta(sheet, row_number, col_ultima, col_intervalo):

    agora = datetime.now(FUSO).strftime("%d/%m/%Y %H:%M")

    intervalo = gerar_intervalo()

    sheet.update_cell(
        row_number,
        col_ultima,
        agora
    )

    sheet.update_cell(
        row_number,
        col_intervalo,
        intervalo
    )
if __name__ == "__main__":

    print("Intervalo:", gerar_intervalo())

    print(
        precisa_coletar(
            "",
            ""
        )
    )
