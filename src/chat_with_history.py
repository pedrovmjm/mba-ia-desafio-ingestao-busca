import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from libs.envs.env_validator import validate_envs
from search import SearchService
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import trim_messages
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict


class ConversationalSearchService:
    """Serviço de busca com histórico de conversação."""

    def __init__(self):
        load_dotenv()
        validate_envs()

        self.search_service = SearchService()
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                REGRAS:
                - SEMPRE mantenha consistência com suas respostas anteriores nesta conversa.
                - Se foi pedido algo relacionado a conversa anterior ou falado anteriormente, desconsidere (ex: "anteriormente", "último", "antes") o CONTEXTO ATUAL e considere o HISTÓRICO.
                - Caso contrário, responda com base no CONTEXTO ATUAL. Com as seguintes regras:
                    - Se a informação não estiver explicitamente no CONTEXTO ATUAL, responda:
                    "Não tenho informações necessárias para responder sua pergunta."
                    - Nunca invente ou use conhecimento externo.
                    - Nunca produza opiniões ou interpretações além do que está escrito.
        
                CONTEXTO ATUAL:
                {context}

                PERGUNTA DO USUÁRIO:""",
                ),
                MessagesPlaceholder("history"),
                ("human", "{input}"),
            ]
        )

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.google_api_key,
            temperature=0.3,
        )

        self.prepare = RunnableLambda(self._prepare_inputs)

        self.chain = self.prepare | self.prompt | self.llm

        self.session_store: Dict[str, InMemoryChatMessageHistory] = {}

        self.conversational_chain = RunnableWithMessageHistory(
            self.chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def _prepare_inputs(self, payload: dict) -> dict:
        """Prepara inputs com contexto da busca e histórico trimado."""
        user_input = payload.get("input", "")
        raw_history = payload.get("history", [])

        context = ""
        if user_input.strip():
            try:
                results = self.search_service.search_documents(user_input)
                context = self.search_service.build_context(results)
            except Exception as e:
                print(f"❌ DEBUG - Erro na busca: {e}")
                context = ""
        else:
            print("⚠️ DEBUG - Input vazio, sem busca de contexto")

        trimmed_history = trim_messages(
            raw_history,
            token_counter=len,
            max_tokens=10,
            strategy="last",
            start_on="human",
            include_system=True,
            allow_partial=False,
        )

        return {"input": user_input, "context": context, "history": trimmed_history}

    def _get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """Obtém ou cria histórico da sessão."""
        if session_id not in self.session_store:
            self.session_store[session_id] = InMemoryChatMessageHistory()
        return self.session_store[session_id]

    def chat(self, message: str, session_id: str = "default") -> str:
        """Processa mensagem com histórico."""
        config = {"configurable": {"session_id": session_id}}

        try:
            response = self.conversational_chain.invoke(
                {"input": message}, config=config
            )
            return response.content
        except Exception as e:
            print(f"❌ DEBUG - Erro ao processar: {e}")
            return f"Erro ao processar mensagem: {e}"

    def clear_history(self, session_id: str = "default"):
        """Limpa histórico da sessão."""
        if session_id in self.session_store:
            self.session_store[session_id].clear()

    def get_history(self, session_id: str = "default") -> list:
        """Obtém histórico da sessão."""
        if session_id in self.session_store:
            return self.session_store[session_id].messages
        return []


def main():
    """Interface CLI com histórico de conversação."""
    print("🤖 Chat com Histórico - Sistema de Busca Semântica")
    print("=" * 50)

    chat_service = ConversationalSearchService()
    session_id = "user_session"

    print("Comandos especiais:")
    print("- 'sair', 'exit', 'quit': Encerrar chat")
    print("- 'limpar', 'clear': Limpar histórico")
    print("- 'historico', 'history': Ver histórico\n")

    print("\n")

    while True:
        try:
            pergunta = input("FAÇA SUA PERGUNTA: ").strip()

            if pergunta.lower() in ["sair", "exit", "quit"]:
                print("Encerrando chat...")
                break

            if pergunta.lower() in ["limpar", "clear"]:
                chat_service.clear_history(session_id)
                print("Histórico limpo!\n")
                continue

            if pergunta.lower() in ["historico", "history"]:
                history = chat_service.get_history(session_id)
                if history:
                    print("\nHistórico da conversa:")
                    for i, msg in enumerate(history[-10:], 1):
                        role = "VOCÊ" if msg.type == "human" else "ASSISTENTE"
                        content = (
                            msg.content[:100] + "..."
                            if len(msg.content) > 100
                            else msg.content
                        )
                        print(f"{i}. {role}: {content}")
                    print()
                else:
                    print("Nenhum histórico encontrado.\n")
                continue

            if not pergunta:
                print("Por favor, digite uma pergunta válida.\n")
                continue
            resposta = chat_service.chat(pergunta, session_id)
            print(f"RESPOSTA DO MODELO: {resposta}\n")

        except KeyboardInterrupt:
            print("\nEncerrando chat...")
            break
        except Exception as e:
            print(f"Erro: {e}\n")


if __name__ == "__main__":
    main()
