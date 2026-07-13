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
# CARREGAR BANCO DE DADOS
# ==================================================

def carregar_banco():

    return banco_sheet.get_all_records()


# ==================================================
# CARREGAR AGULHA
# ==================================================

def carregar_agulha():

    return agulha_sheet.get_all_records()


# ==================================================
# CARREGAR CONFIGURAÇÕES
# ==================================================

def carregar_config():

    valores = config_sheet.get_all_values()

    configuracoes = {}

    for linha in valores[1:]:

        if len(linha) < 2:
            continue

        chave = linha[0].strip().upper()
        valor = linha[1].strip()

        # BOOLEAN
        if valor.upper() in ("TRUE", "FALSE"):

            configuracoes[chave] = (
                valor.upper() == "TRUE"
            )

            continue

        # INTEIRO
        try:

            configuracoes[chave] = int(valor)

            continue

        except:
            pass

        # FLOAT
        try:

            configuracoes[chave] = float(
                valor.replace(",", ".")
            )

            continue

        except:
            pass

        # TEXTO
        configuracoes[chave] = valor

    return configuracoes


# ==================================================
# COLUNAS
# ==================================================

def obter_colunas(aba):

    cabecalho = aba.row_values(1)

    return {

        coluna.strip().upper(): indice + 1

        for indice, coluna in enumerate(cabecalho)

    }


# ==================================================
# ESCREVER AGULHA
# ==================================================

def escrever_agulha(produtos):

    """
    Recebe uma lista contendo:

    POSIÇÃO
    ROW_BANCO
    PRODUTO
    ID
    URL_ORIGEM
    LINK_AFILIADO
    PREÇO
    PREÇO_ANTIGO
    DESCONTO
    ESTOQUE
    ULTIMA_ATUALIZAÇÃO
    """

    if not produtos:
        return

    agulha_sheet.update(
        f"A2:K{len(produtos)+1}",
        produtos
    )


# ==================================================
# SINCRONIZA AGULHA -> BANCO
# ==================================================

def sincronizar_agulha_para_banco():

    agulha = carregar_agulha()

    colunas = obter_colunas(banco_sheet)

    for produto in agulha:

        try:

            row = int(produto["ROW_BANCO"])

        except:

            continue

        banco_sheet.update_cell(
            row,
            colunas["PREÇO"],
            produto.get("PREÇO", "")
        )

        banco_sheet.update_cell(
            row,
            colunas["PREÇO_ANTIGO"],
            produto.get("PREÇO_ANTIGO", "")
        )

        banco_sheet.update_cell(
            row,
            colunas["DESCONTO"],
            produto.get("DESCONTO", "")
        )

        banco_sheet.update_cell(
            row,
            colunas["ESTOQUE"],
            produto.get("ESTOQUE", "")
        )

        banco_sheet.update_cell(
            row,
            colunas["ULTIMA_ATUALIZAÇÃO"],
            produto.get("ULTIMA_ATUALIZAÇÃO", "")
        )


# ==================================================
# LOCALIZA LINHA PELO ID
# ==================================================

def localizar_row_por_id(id_produto):

    produtos = carregar_banco()

    for indice, produto in enumerate(produtos, start=2):

        if str(produto.get("ID", "")).strip() == str(id_produto).strip():

            return indice

    return None


# ==================================================
# ATUALIZAR CÉLULA
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
# ATUALIZAR VÁRIAS COLUNAS
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

    print()

    banco = carregar_banco()

    print(f"BANCO_DADOS: {len(banco)} produtos")

    agulha = carregar_agulha()

    print(f"AGULHA: {len(agulha)} produtos")

    print()

    print("CONFIGURAÇÕES:")

    config = carregar_config()

    for chave, valor in config.items():

        print(f"{chave}: {valor}")

    print()

    print("COLUNAS BANCO_DADOS")

    print(obter_colunas(banco_sheet))

    print()

    print("COLUNAS AGULHA")

    print(obter_colunas(agulha_sheet))

    print()

    print("Sheets inicializado com sucesso.")
