from coletores.magalu import coletar_magalu


def coletar(url: str):

    if "magazinevoce" in url or "magazineluiza" in url:
        return coletar_magalu(url)

    raise ValueError("Loja não suportada.")
