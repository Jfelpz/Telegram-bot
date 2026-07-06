import random
from cache import precisa_coletar, registrar_coleta
from config import MAX_COLETAS


# ---------------------------------------------------
# SIMULAÇÃO / FUTURO AMAPULSE
# ---------------------------------------------------
def atualizar_produto(produto):

    try:
        preco = float(produto.get("preco_atual", 100))
    except:
        preco = 100

    produto["preco_atual"] = preco - random.randint(1, 20)

    return produto


# ---------------------------------------------------
# VALIDAÇÃO DE DADOS
# ---------------------------------------------------
def produto_valido(produto):
    """
    Evita crash por linha vazia ou dados quebrados
    """

    if not produto:
        return False

    if "preco_atual" not in produto:
        return False

    return True


# ---------------------------------------------------
# COLETOR PRINCIPAL
# ---------------------------------------------------
def coletar_produtos(sheet, rows, colunas):

    print("=== INICIANDO COLETOR ===")

    random.shuffle(rows)

    coletados = 0

    for i, row in enumerate(rows, start=2):

        if coletados >= MAX_COLETAS:
            print("Limite de coleta atingido.")
            break

        try:
            ultima_coleta = row.get(colunas["ultima_coleta"], "")
            intervalo = row.get(colunas["intervalo"], "")

            # cache decide se atualiza
            if not precisa_coletar(ultima_coleta, intervalo):
                continue

            print(f"Atualizando produto linha {i}...")

            # valida produto antes de tudo
            if not produto_valido(row):
                print(f"Linha {i} inválida, ignorando.")
                continue

            # atualiza produto (futuro Amapulse)
            produto_atualizado = atualizar_produto(row)

            # atualiza preço
            sheet.update_cell(
                i,
                colunas["preco"],
                produto_atualizado["preco_atual"]
            )

            # registra coleta
            registrar_coleta(
                sheet,
                i,
                colunas["ultima_coleta"],
                colunas["intervalo"]
            )

            coletados += 1

        except Exception as e:
            print(f"[ERRO] Linha {i}: {e}")

    print(f"=== FINALIZADO | {coletados} produtos atualizados ===")


# ---------------------------------------------------
# TESTE LOCAL
# ---------------------------------------------------
if __name__ == "__main__":
    print("Coletor pronto (modo teste).")
