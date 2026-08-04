"""
=========================================
TESTE DE CONEXÃO MERCADO LIVRE
=========================================
"""

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao PATH
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from coletores.mercadolivre import MercadoLivre


def main():

    print("=" * 60)
    print("TESTE DE CONEXÃO COM O MERCADO LIVRE")
    print("=" * 60)

    ml = MercadoLivre()

    try:

        usuario = ml.meus_dados()

        print("\n✅ Conexão realizada com sucesso!\n")

        print(f"ID: {usuario.get('id')}")
        print(f"Nickname: {usuario.get('nickname')}")
        print(f"País: {usuario.get('country_id')}")
        print(f"Site: {usuario.get('site_id')}")

    except Exception as erro:

        print("\n❌ Erro ao conectar com a API:\n")
        print(erro)


if __name__ == "__main__":
    main()
