import random
from cache import precisa_coletar, registrar_coleta
from config import MAX_COLETAS


# ---------------------------------------------------
# SIMULAÇÃO: AQUI ENTRA O AMAPULSE / SCRAPER FUTURO
# ---------------------------------------------------
def atualizar_produto(produto):
    """
    FUTURO: Aqui você vai chamar Amapulse ou PA-API.
    Hoje é apenas simulação.
    """

    # Simula novo preço
    produto["preco_atual"] = produto.get("preco_atual", 100) - random.randint(1, 20)

    return produto


# ---------------------------------------------------
# COLETOR PRINCIPAL
# ---------------------------------------------------
def coletar_produtos(sheet, rows, colunas):
    """
    sheet: objeto Google Sheets
    rows: lista de linhas da planilha
    colunas: dict com posições das colunas
    """

    print("=== INICIANDO COLETOR ===")

    # 1. embaralha produtos (evita padrão previsível)
    random.shuffle(rows)

    coletados = 0

    # 2. percorre produtos
    for i, row in enumerate(rows, start=2):  # start=2 (linha real da planilha)

        if coletados >= MAX_COLETAS:
            print("Limite de coleta atingido.")
            break

        ultima_coleta = row[colunas["ultima_coleta"]]
        intervalo = row[colunas["intervalo"]]

        # 3. consulta cache
        if not precisa_coletar(ultima_coleta, intervalo):
            continue

        try:
            print(f"Atualizando produto linha {i}...")

            # 4. atualiza produto (Amapulse futuramente)
            produto_atualizado = atualizar_produto(row)

            # 5. salva novo preço (exemplo)
            sheet.update_cell(i, colunas["preco"], produto_atualizado["preco_atual"])

            # 6. registra coleta (cache inteligente)
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
# TESTE LOCAL (opcional)
# ---------------------------------------------------
if __name__ == "__main__":

    print("Coletor pronto (modo teste).")
