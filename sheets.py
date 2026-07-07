import json
import gspread

from google.oauth2.service_account import Credentials

from config import SHEET_ID, GOOGLE_CREDENTIALS


# ==================================================
# CONFIGURAÇÃO GOOGLE
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
    Retorna todos os produtos da aba MENU
    como lista de dicionários.
    """

    return sheet.get_all_records()



# ==================================================
# MAPEAR COLUNAS AUTOMATICAMENTE
# ==================================================

def carregar_colunas():

    """
    Encontra as posições das colunas pelo nome.
    Evita depender de posição fixa.
    """

    cabecalhos = sheet.row_values(1)


    colunas = {

        "preco":
            cabecalhos.index("PREÇO") + 1,


        "preco_antigo":
            cabecalhos.index("PREÇO_ANTIGO") + 1,


        "ultima_atualizacao":
            cabecalhos.index("ULTIMA_ATUALIZAÇÃO") + 1,


        "ultima_coleta_api":
            cabecalhos.index("ULTIMA_COLETA_API") + 1,


        "intervalo_api":
            cabecalhos.index("INTERVALO_COLETA_API") + 1,

    }


    return colunas



# ==================================================
# TESTE DE CONEXÃO
# ==================================================

if __name__ == "__main__":


    print("Conectado ao Google Sheets")


    produtos = carregar_produtos()


    print(
        f"Produtos encontrados: {len(produtos)}"
    )


    colunas = carregar_colunas()


    print(
        "Colunas:"
    )

    print(colunas)
