import json
import random
import string

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
# GERAÇÃO DE ID ÚNICO
# ==================================================

# Iniciais conhecidas por loja. Lojas não listadas aqui usam
# automaticamente as 3 primeiras letras do nome (fallback).
INICIAIS_LOJA = {
    "MAGALU": "MAG",
    "ALIEXPRESS": "ALI",
    "MERCADO_LIVRE": "MEL",
    "MERCADO LIVRE": "MEL",
    "SHOPEE": "SHO",
    "KABUM": "KAB",
    "SAMSUNG": "SAM",
}


def obter_iniciais_loja(loja: str) -> str:

    loja_normalizada = str(loja).strip().upper()

    if loja_normalizada in INICIAIS_LOJA:
        return INICIAIS_LOJA[loja_normalizada]

    # Fallback: 3 primeiras letras do nome da loja
    apenas_letras = "".join(
        c for c in loja_normalizada if c.isalpha()
    )

    return (apenas_letras[:3] or "LOJ")


def gerar_codigo_aleatorio(tamanho: int = 6) -> str:

    caracteres = string.ascii_uppercase + string.digits

    return "".join(
        random.choice(caracteres)
        for _ in range(tamanho)
    )


def gerar_id_unico(loja: str, categoria: str, ids_existentes: set) -> str:
    """
    Gera um ID no formato INICIAISCODIGOCAT (ex: MAG2T5X4QCEL),
    garantindo que não colide com nenhum ID já existente
    na planilha (ids_existentes).
    """

    iniciais = obter_iniciais_loja(loja)

    apenas_letras_categoria = "".join(
        c for c in str(categoria).strip().upper() if c.isalpha()
    )

    categoria_normalizada = apenas_letras_categoria[:3] or "GER"

    while True:

        codigo = gerar_codigo_aleatorio()

        novo_id = f"{iniciais}{codigo}{categoria_normalizada}"

        if novo_id not in ids_existentes:

            ids_existentes.add(novo_id)

            return novo_id


def garantir_ids(produtos: list, colunas: dict) -> int:
    """
    Percorre os produtos carregados da planilha e, para cada
    linha sem valor na coluna ID, gera um ID único e grava
    direto na planilha. Atualiza também o dicionário 'produto'
    em memória, para uso imediato no restante da execução.

    Retorna a quantidade de IDs novos gerados.
    """

    if "ID" not in colunas:

        print(
            "Aviso: coluna ID não encontrada na planilha; "
            "geração de ID pulada."
        )

        return 0

    ids_existentes = {
        str(produto.get("ID", "")).strip()
        for produto in produtos
        if str(produto.get("ID", "")).strip()
    }

    gerados = 0

    for produto in produtos:

        id_atual = str(produto.get("ID", "")).strip()

        if id_atual:
            continue

        loja = produto.get("LOJA", "")
        categoria = produto.get("CATEGORIA", "")

        novo_id = gerar_id_unico(loja, categoria, ids_existentes)

        atualizar_celula(
            banco_sheet,
            produto["ROW_NUMBER"],
            colunas["ID"],
            novo_id
        )

        produto["ID"] = novo_id

        gerados += 1

        print(f"[ID] Linha {produto['ROW_NUMBER']}: {novo_id}")

    return gerados


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
