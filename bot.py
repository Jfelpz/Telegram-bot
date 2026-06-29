from sheets import sheet, config_sheet
from telegram import enviar
from logic import processar
import time
import os


# ==========================
# CONTROLE DE TEMPO (opcional aqui se ainda quiser manter global)
# ==========================

def main():

    print("🚀 BOT INICIADO")

    processar(enviar)

    print("✅ EXECUÇÃO FINALIZADA")


if __name__ == "__main__":
    main()
