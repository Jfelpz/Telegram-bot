from datetime import datetime
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Fortaleza")


# ==================================================
# PESOS DAS PRIORIDADES
# ==================================================

PESO_PRIORIDADE = {
    "ALTA": 100,
    "MÉDIA": 50,
    "MEDIA": 50,
    "BAIXA": 10
}


# ==================================================
# PESOS DAS CATEGORIAS
# ==================================================

PESO_CATEGORIA = {
    "GPU": 50,
    "PLACA DE VIDEO": 50,
    "PLACA DE VÍDEO": 50,

    "CPU": 45,
    "PROCESSADOR": 45,

    "SSD": 35,

    "MEMÓRIA": 25,
    "MEMORIA": 25,
    "RAM": 25,

    "PLACA-MÃE": 20,
    "PLACA MAE": 20,

    "MONITOR": 15,
    "NOTEBOOK": 15,

    "MOUSE": 5,
    "TECLADO": 5,
    "HEADSET": 5
}


# ==================================================
# CONVERTE DESCONTO
# ==================================================

def desconto_para_float(valor):

    try:
        return float(
            str(valor)
            .replace("%", "")
            .replace(",", ".")
        )

    except:
        return 0


# ==================================================
# BÔNUS POR RECÊNCIA
# ==================================================

def calcular_bonus_recencia(data):

    if not data:
        return 0

    try:

        ultima = datetime.strptime(
            data,
            "%d/%m/%Y %H:%M"
        ).replace(
            tzinfo=FUSO
        )

    except:
        return 0

    dias = (
        datetime.now(FUSO) - ultima
    ).days

    if dias <= 1:
        return 10

    elif dias <= 3:
        return 7

    elif dias <= 7:
        return 4

    return 0


# ==================================================
# SCORE
# ==================================================

def calcular_score(produto):

    score = 0

    prioridade = str(
        produto.get("PRIORIDADE", "")
    ).strip().upper()

    categoria = str(
        produto.get("CATEGORIA", "")
    ).strip().upper()

    desconto = desconto_para_float(
        produto.get("DESCONTO", 0)
    )

    score += PESO_PRIORIDADE.get(
        prioridade,
        0
    )

    score += PESO_CATEGORIA.get(
        categoria,
        5
    )

    score += desconto

    score += calcular_bonus_recencia(
        produto.get(
            "ULTIMA_ATUALIZAÇÃO",
            ""
        )
    )

    return score


# ==================================================
# RANKING
# ==================================================

def gerar_ranking(produtos):

    elegiveis = []

    for produto in produtos:

        nome = produto.get(
            "PRODUTO",
            "SEM NOME"
        )

        # ---------------------------------
        # CHECKBOX ATIVO
        # ---------------------------------

        ativo = str(
            produto.get("ATIVO", "")
        ).strip().upper()

        if ativo not in (
            "TRUE",
            "VERDADEIRO",
            "SIM",
            "1"
        ):

            print(f"⏸ Produto desativado: {nome}")

            continue


        # ---------------------------------
        # ESTOQUE
        # ---------------------------------

        estoque = str(
            produto.get("ESTOQUE", "")
        ).strip().upper()

        if estoque != "EM ESTOQUE":

            print(f"📦 Sem estoque: {nome}")

            continue


        # ---------------------------------
        # STATUS
        # ---------------------------------

        status = str(
            produto.get("STATUS", "")
        ).strip().upper()

        if status == "ENVIADO":

            print(f"✅ Já enviado: {nome}")

            continue


        # ---------------------------------
        # SCORE
        # ---------------------------------

        produto["SCORE"] = calcular_score(produto)

        elegiveis.append(produto)


    elegiveis.sort(
        key=lambda x: x["SCORE"],
        reverse=True
    )

    return elegiveis


# ==================================================
# TESTE
# ==================================================

if __name__ == "__main__":

    produtos = [

        {
            "PRODUTO": "RTX 5070",
            "CATEGORIA": "GPU",
            "PRIORIDADE": "ALTA",
            "DESCONTO": "15%",
            "ATIVO": "TRUE",
            "ESTOQUE": "Em estoque",
            "STATUS": "",
            "ULTIMA_ATUALIZAÇÃO": "05/07/2026 10:30"
        },

        {
            "PRODUTO": "Ryzen 9700X",
            "CATEGORIA": "CPU",
            "PRIORIDADE": "ALTA",
            "DESCONTO": "10%",
            "ATIVO": "TRUE",
            "ESTOQUE": "Atualmente indisponível",
            "STATUS": "",
            "ULTIMA_ATUALIZAÇÃO": "04/07/2026 09:20"
        },

        {
            "PRODUTO": "SSD Kingston",
            "CATEGORIA": "SSD",
            "PRIORIDADE": "MÉDIA",
            "DESCONTO": "25%",
            "ATIVO": "TRUE",
            "ESTOQUE": "Em estoque",
            "STATUS": "",
            "ULTIMA_ATUALIZAÇÃO": "01/07/2026 08:00"
        },

        {
            "PRODUTO": "Mouse Logitech",
            "CATEGORIA": "MOUSE",
            "PRIORIDADE": "BAIXA",
            "DESCONTO": "40%",
            "ATIVO": "FALSE",
            "ESTOQUE": "Em estoque",
            "STATUS": "",
            "ULTIMA_ATUALIZAÇÃO": "05/07/2026 12:00"
        }

    ]

    ranking = gerar_ranking(produtos)

    print("\n===== RANKING =====\n")

    for produto in ranking:

        print(
            f"{produto['PRODUTO']} | Score: {produto['SCORE']}"
        )
