if __name__ == "__main__":

    print("=== TESTE DO CACHE ===")

    print("Intervalo:", gerar_intervalo())

    print(
        "Sem coleta:",
        precisa_coletar("", "")
    )

    from datetime import datetime
    from zoneinfo import ZoneInfo

    agora = datetime.now(ZoneInfo("America/Fortaleza")).strftime("%d/%m/%Y %H:%M")

    print(
        "Coletado agora:",
        precisa_coletar(
            agora,
            60
        )
    )
