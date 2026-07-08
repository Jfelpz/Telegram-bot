# ranking.py

# ==================================================
# PESOS DAS PRIORIDADES
# ==================================================

PESO_PRIORIDADE = {
    "ALTA": 100,
    "MÉDIA": 50,
    "MEDIA": 50,   # evita problemas com acento
    "BAIXA": 10
}


# ==================================================
# PESOS DAS CATEGORIAS
# ==================================================

PESO_CATEGORIA = {
    "GPU": 50,
    "PLACA DE VIDEO": 50,
    "CPU": 45,
    "PROCESSADOR": 45,
    "SSD": 35,
    "MEMÓRIA": 25,
    "MEMORIA": 25,
    "RAM": 25,
    "PLACA-MÃE": 20,
    "PLACA MAE": 20
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
# CALCULA SCORE
# ==================================================

def calcular_score(produto):

    score = 0

    # -------------------------
    # PRIORIDADE
    # -------------------------

    prioridade = str(
        produto.get("PRIORIDADE", "")
    ).strip().upper()

    score += PESO_PRIORIDADE.get(
        prioridade,
        0
    )


    # -------------------------
    # CATEGORIA
    # -------------------------

    categoria = str(
        produto.get("CATEGORIA", "")
    ).strip().upper()

    score += PESO_CATEGORIA.get(
        categoria,
        5
    )


    # -------------------------
    # DESCONTO
    # -------------------------

    desconto = desconto_para_float(
        produto.get("DESCONTO", 0)
    )

    score += desconto


    return score


# ==================================================
# RANKING
# ==================================================

def gerar_ranking(produtos):

    elegiveis = []

    for produto in produtos:

        ativo = str(
            produto.get("ATIVO", "")
        ).strip().upper()

        status = str(
            produto.get("STATUS", "")
        ).strip().upper()


        if ativo not in ["SIM", "TRUE", "1"]:
            continue


        if status == "ENVIADO":
            continue


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
            "STATUS": "",
            "ATIVO": "SIM"
        },

        {
            "PRODUTO": "Mouse",
            "CATEGORIA": "MOUSE",
            "PRIORIDADE": "BAIXA",
            "DESCONTO": "40%",
            "STATUS": "",
            "ATIVO": "SIM"
        }

    ]


    ranking = gerar_ranking(produtos)


    for p in ranking:

        print(
            p["PRODUTO"],
            p["SCORE"]
        )
