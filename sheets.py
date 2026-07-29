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
config_sheet = spreadsheet.worksheet("CONFIG")


# ==================================================
# CARREGAR BANCO DE DADOS
# ==================================================

def carregar_banco():
    """
    Carrega os produtos preservando o número da linha
    da planilha.
    """

    valores = banco_sheet.get_all_values()

    if len(valores) <= 1:
        return []

    cabecalho = valores[0]

    produtos = []

    for numero_linha, linha in enumerate(valores[1:], start=2):

        produto = {}

        for indice, coluna in enumerate(cabecalho):

            if indice < len(linha):
                produto[coluna] = linha[indice]
            else:
                produto[coluna] = ""

        produto["ROW_NUMBER"] = numero_linha

        produtos.append(produto)

    return produtos


# ==================================================
# CONFIGURAÇÕES
# ==================================================

def carregar_config():

    valores = config_sheet.get_all_values()

    configuracoes = {}

    for linha in valores[1:]:

        if len(linha) < 2:
            continue

        chave = linha[0].strip().upper()
        valor = linha[1].strip()

        # Boolean
        if valor.upper() in ("TRUE", "FALSE"):

            configuracoes[chave] = (
                valor.upper() == "TRUE"
            )

            continue

        # Inteiro
        try:
            configuracoes[chave] = int(valor)
            continue
        except:
            pass

        # Float
        try:
            configuracoes[chave] = float(
                valor.replace(",", ".")
            )
            continue
        except:
            pass

        configuracoes[chave] = valor

    return configuracoes


# ==================================================
# MAPA DAS COLUNAS
# ==================================================

def obter_colunas(aba):

    cabecalho = aba.row_values(1)

    return {

        coluna.strip().upper(): indice + 1

        for indice, coluna in enumerate(cabecalho)

    }


# ==================================================
# LOCALIZA LINHA PELO ID
# ==================================================

def localizar_row_por_id(id_produto):

    produtos = carregar_banco()

    for produto in produtos:

        if str(produto.get("ID", "")).strip() == str(id_produto).strip():

            return produto["ROW_NUMBER"]

    return None


# ==================================================
# ATUALIZAR UMA CÉLULA
# ==================================================

def atualizar_celula(
    aba,
    linha,
    coluna,
    valor
):

    aba.update_cell(
        linha,
        coluna,
        valor
    )


# ==================================================
# ATUALIZAR VÁRIAS CÉLULAS
# ==================================================

def atualizar_linha(
    aba,
    linha,
    dados
):

    for coluna, valor in dados.items():

        aba.update_cell(
            linha,
            coluna,
            valor
        )


# ==================================================
# LER LINHAS
# ==================================================

def ler_linhas(aba):

    return aba.get_all_values()


# ==================================================
# TESTE
# ==================================================

if __name__ == "__main__":

    print("=" * 60)
    print("GOOGLE SHEETS CONECTADO")
    print("=" * 60)

    produtos = carregar_banco()

    print(f"Produtos encontrados: {len(produtos)}")

    print()

    print("CONFIGURAÇÕES")

    config = carregar_config()

    for chave, valor in config.items():

        print(f"{chave}: {valor}")

    print()

    print("COLUNAS")

    print(obter_colunas(banco_sheet))

    print()

    print("Sheets inicializado com sucesso.")
