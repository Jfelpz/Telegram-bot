from sheets import (
    sheet,
    carregar_produtos,
    carregar_colunas
)

from coletor import coletar_produtos



def main():

    print(
        "=== EXECUTANDO RUN COLETOR ==="
    )


    produtos = carregar_produtos()


    colunas = carregar_colunas()


    coletar_produtos(
        sheet,
        produtos,
        colunas
    )


    print(
        "=== COLETOR FINALIZADO ==="
    )



if __name__ == "__main__":

    main()
