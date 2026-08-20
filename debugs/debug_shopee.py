from coletores.shopee import ShopeeCollector


print("=" * 50)
print("TESTANDO API DA SHOPEE")
print("=" * 50)


def main():

    # ==========================================================
    # COLE A URL DE UM PRODUTO REAL DA SHOPEE AQUI
    # ==========================================================

    url = (
        "COLE_AQUI_UMA_URL_DE_PRODUTO_DA_SHOPEE"
    )

    print()
    print(f"URL utilizada: {url}")
    print()

    # ==========================================================
    # INICIALIZA O COLETOR
    # ==========================================================

    try:

        coletor = ShopeeCollector()

    except Exception as erro:

        print("ERRO AO INICIALIZAR O COLETOR")
        print(erro)

        return

    # ==========================================================
    # REALIZA A COLETA
    # ==========================================================

    resultado = coletor.coletar(url)

    # ==========================================================
    # MOSTRA O RESULTADO
    # ==========================================================

    print()
    print("=" * 50)
    print("RESULTADO DA COLETA")
    print("=" * 50)
    print()

    for chave, valor in resultado.items():

        print(f"{chave}: {valor}")

    print()
    print("=" * 50)

    # ==========================================================
    # RESULTADO FINAL
    # ==========================================================

    if resultado.get("erro"):

        print("❌ TESTE FINALIZADO COM ERRO")

        print(
            "Mensagem:",
            resultado.get("mensagem")
        )

    else:

        print("✅ TESTE REALIZADO COM SUCESSO")


if __name__ == "__main__":

    main()
