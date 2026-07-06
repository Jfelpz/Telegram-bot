from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import random

FUSO = ZoneInfo("America/Fortaleza")

# Intervalo mínimo e máximo entre coletas (em minutos)
MIN_INTERVALO = 60
MAX_INTERVALO = 90


# ---------------------------------------------------
# 1. GERA INTERVALO ALEATÓRIO POR PRODUTO
# ---------------------------------------------------
def gerar_intervalo():
    """
    Gera um intervalo aleatório entre MIN e MAX.
    Cada produto terá seu próprio intervalo dinâmico.
    """
    return random.randint(MIN_INTERVALO, MAX_INTERVALO)


# ---------------------------------------------------
# 2. VERIFICA SE PRECISA COLETAR
# ---------------------------------------------------
def precisa_coletar(ultima_coleta, intervalo):
    """
    Retorna True se o produto precisa ser atualizado.
    Usa intervalo individual por produto.
    """

    if not ultima_coleta:
        return True

    try:
        ultima = datetime.strptime(
            ultima_coleta,
            "%d/%m/%Y %H:%M"
        ).replace(tzinfo=FUSO)

    except Exception:
        return True

    try:
        minutos = int(intervalo)
    except Exception:
        # fallback inteligente (não quebra o sistema)
        minutos = gerar_intervalo()

    proxima = ultima + timedelta(minutes=minutos)

    return datetime.now(FUSO) >= proxima


# ---------------------------------------------------
# 3. REGISTRA COLETA NA PLANILHA
# ---------------------------------------------------
def registrar_coleta(sheet, row_number, col_ultima, col_intervalo):
    """
    Atualiza:
    - última coleta
    - novo intervalo aleatório (cache individual)
    """

    agora = datetime.now(FUSO).strftime("%d/%m/%Y %H:%M")
    intervalo = gerar_intervalo()

    try:
        sheet.update_cell(row_number, col_ultima, agora)
        sheet.update_cell(row_number, col_intervalo, intervalo)

    except Exception as e:
        print(f"[CACHE ERROR] Falha ao registrar coleta: {e}")


# ---------------------------------------------------
# 4. UTILITÁRIO DE TESTE
# ---------------------------------------------------
if __name__ == "__main__":

    print("=== TESTE DO CACHE ===")

    print("Intervalo gerado:", gerar_intervalo())

    print("Sem dados:", precisa_coletar("", ""))

    agora = datetime.now(FUSO).strftime("%d/%m/%Y %H:%M")

    print("Coletado agora:", precisa_coletar(agora, 60))
