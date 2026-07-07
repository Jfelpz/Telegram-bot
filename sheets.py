import json
import gspread

from google.oauth2.service_account import Credentials

from config import SHEET_ID, GOOGLE_CREDENTIALS


# ==================================================
# CONFIGURAÇÃO GOOGLE SHEETS
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


sheet = spreadsheet.worksheet("MENU")
config_sheet = spreadsheet.worksheet("CONFIG")



# ==================================================
# CARREGAR PRODUTOS
# ==================================================

def carregar_produtos():

    """
    Retorna todos os produtos da aba MENU.
    Cada linha vira um dicionário.
    """

    return sheet.get_all_records()



# ==================================================
# LOCALIZAR COLUNAS
# ==================================================

def carregar_colunas():

    """
    Busca as colunas pelo nome.
    Evita depender da posição fixa.
    """

    cabecalhos = sheet.row_values(1)


    colunas = {

        "ultima_coleta_api":
            cabecalhos.index(
                "ULTIMA_COLETA_API"
            ) + 1,


        "intervalo_api":
            cabecalhos.index(
                "INTERVALO_COLETA_API"
            ) + 1,

    }


    return colunas



# ==================================================
# TESTE
# ==================================================

if __name__ == "__main__":

    print("Google Sheets conectado.")

    produtos = carregar_produtos()

    print(
        f"Produtos encontrados: {len(produtos)}"
    )


    print(
        carregar_colunas()
    )
