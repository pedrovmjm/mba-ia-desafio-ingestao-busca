import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search import SearchService
from dotenv import load_dotenv
from libs.envs.env_validator import validate_envs


def main():
    load_dotenv()
    validate_envs()

    chain = SearchService()
    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    print("Faça sua pergunta (digite 'sair' para encerrar):\n")
    while True:
        pergunta = input("FAÇA SUA PERGUNTA: ").strip()
        if pergunta.strip().lower() in ["sair", "exit", "quit"]:
            print("Encerrando chat.")
            break
        resposta = chain.answer(pergunta)
        print(f"RESPOSTA DO MODELO: {resposta}\n")


if __name__ == "__main__":
    main()
