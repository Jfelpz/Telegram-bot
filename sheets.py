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

    """
    Retorna todos os produtos do BANCO_DADOS.
    """

    return banco_sheet.get_all_records()


# ==================================================
# CARREGAR AGULHA
# ==================================================

def carregar_agulha():

    """
    Retorna todos os produtos presentes
    na aba AGULHA.
    """

    return agulha_sheet.get_all_records()


# ==================================================
# CARREGAR CONFIGURAÇÕES
# ==================================================

def carregar_config():

    """
    Lê a aba CONFIG.

    Estrutura:

    CONFIGURAÇÃO | VALOR

    Converte automaticamente:

    TRUE/FALSE -> bool
    15 -> int
    15.5 -> float

    Horários permanecem string.
    """

    valores = config_sheet.get_all_values()

    configuracoes = {}

    for linha in valores[1:]:

        if len(linha) < 2:
            continue

        chave = linha[0].strip().upper()

        valor = linha[1].strip()

        # ------------------------
        # BOOLEAN
        # ------------------------

        if valor.upper() in ("TRUE", "FALSE"):

            configuracoes[chave] = (
                valor.upper() == "TRUE"
            )

            continue

        # ------------------------
        # INTEIRO
        # ------------------------

        try:

            configuracoes[chave] = int(valor)

            continue

        except:

            pass

        # ------------------------
        # FLOAT
        # ------------------------

        try:

            configuracoes[chave] = float(
                valor.replace(",", ".")
            )

            continue

        except:

            pass

        # ------------------------
        # TEXTO
        # ------------------------

        configuracoes[chave] = valor

    return configuracoes


# ==================================================
# COLUNAS
# ==================================================

def obter_colunas(aba):

    """
    Retorna:

    {
        "ID":1,
        "PRODUTO":2,
        ...
    }
    """

    cabecalho = aba.row_values(1)

    return {

        coluna.strip().upper(): indice + 1

        for indice, coluna in enumerate(cabecalho)

    }


# ==================================================
# LIMPA AGULHA
# ==================================================

def limpar_agulha():

    """
    Remove todos os produtos da AGULHA.

    Mantém somente o cabeçalho.
    """

    total = len(
        agulha_sheet.get_all_values()
    )

    if total <= 1:
        return

    agulha_sheet.batch_clear(
        [f"A2:H{total}"]
    )


# ==================================================
# ESCREVER PRODUTOS NA AGULHA
# ==================================================

def escrever_agulha(produtos):

    """
    Escreve uma lista de produtos na AGULHA.

    Espera receber uma lista de listas.

    Exemplo:

    [
        [1, id, url, preco...],
        [2, id, url, preco...]
    ]
    """

    limpar_agulha()

    if not produtos:
        return

    agulha_sheet.update(
        f"A2:H{len(produtos)+1}",
        produtos
    )


# ==================================================
# ATUALIZA UMA CÉLULA
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
# LER LINHAS
# ==================================================

def ler_linhas(aba):

    return aba.get_all_values()


# ==================================================
# TESTE
# ==================================================

if __name__ == "__main__":

    print("=" * 50)
    print("GOOGLE SHEETS CONECTADO")
    print("=" * 50)

    print()

    banco = carregar_banco()

    print(
        f"BANCO_DADOS: {len(banco)} produtos"
    )

    agulha = carregar_agulha()

    print(
        f"AGULHA: {len(agulha)} produtos"
    )

    print()

    print("CONFIG:")

    config = carregar_config()

    for chave, valor in config.items():

        print(
            f"{chave}: {valor}"
        )

    print()

    print("COLUNAS BANCO_DADOS")

    print(
        obter_colunas(
            banco_sheet
        )
    )

    print()

    print("COLUNAS AGULHA")

    print(
        obter_colunas(
            agulha_sheet
        )
    )

    print()

    print("Teste concluído.")
