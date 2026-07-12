import json
import gspread

from google.oauth2.service_account import Credentials

from config import SHEET_ID, GOOGLE_CREDENTIALS


# ==================================================
# GOOGLE SHEETS
# ==================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

credentials = Credentials.from_service_account_info(
    json.loads(GOOGLE_CREDENTIALS),
    scopes=SCOPES
)

client = gspread.authorize(credentials)

spreadsheet = client.open_by_key(SHEET_ID)


# ==================================================
# ABAS
# ==================================================

banco_sheet = spreadsheet.worksheet("BANCO_DADOS")
agulha_sheet = spreadsheet.worksheet("AGULHA")
config_sheet = spreadsheet.worksheet("CONFIG")


# ==================================================
# CARREGA BANCO DE DADOS
# ==================================================

def carregar_banco():

    """
    Retorna todos os produtos do BANCO_DADOS.
    """

    return banco_sheet.get_all_records()


# ==================================================
# CARREGA AGULHA
# ==================================================

def carregar_agulha():

    """
    Retorna os produtos presentes na AGULHA.
    """

    return agulha_sheet.get_all_records()


# ==================================================
# CONFIG
# ==================================================

def carregar_config():

    """
    Lê a aba CONFIG e devolve um dicionário.

    Estrutura esperada:

    CONFIGURAÇÃO | VALOR
    """

    valores = config_sheet.get_all_values()

    configuracoes = {}

    for linha in valores[1:]:

        if len(linha) < 2:
            continue

        chave = linha[0].strip().upper()

        valor = linha[1]

        configuracoes[chave] = valor

    return configuracoes


# ==================================================
# CABEÇALHOS
# ==================================================

def obter_colunas(sheet):

    """
    Retorna um dicionário contendo:

    {
        "ID":1,
        "PRODUTO":2,
        ...
    }
    """

    cabecalho = sheet.row_values(1)

    return {

        coluna.strip().upper(): indice + 1

        for indice, coluna in enumerate(cabecalho)

    }


# ==================================================
# LIMPA AGULHA
# ==================================================

def limpar_agulha():

    """
    Remove todos os produtos da AGULHA,
    mantendo apenas o cabeçalho.
    """

    total_linhas = len(agulha_sheet.get_all_values())

    if total_linhas > 1:

        agulha_sheet.batch_clear(
            [f"A2:H{total_linhas}"]
        )


# ==================================================
# TESTE
# ==================================================

if __name__ == "__main__":

    print("===================================")
    print("Google Sheets conectado")
    print("===================================\n")

    print(
        f"Produtos no BANCO_DADOS: {len(carregar_banco())}"
    )

    print(
        f"Produtos na AGULHA: {len(carregar_agulha())}"
    )

    print("\nConfigurações:")

    print(carregar_config())

    print("\nColunas BANCO_DADOS:")

    print(
        obter_colunas(banco_sheet)
    )

    print("\nColunas AGULHA:")

    print(
        obter_colunas(agulha_sheet)
    )
