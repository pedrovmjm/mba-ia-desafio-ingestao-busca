import os
from typing import List, Tuple
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.documents import Document


class SearchService:
    """Serviço simples de busca semântica."""

    def __init__(self):
        self.db_url: str = os.getenv("DATABASE_URL", "")
        self.collection_name: str = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")
        self.google_api_key: str = os.getenv("GOOGLE_API_KEY", "")

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", google_api_key=self.google_api_key
        )

        self.vectorstore = PGVector(
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            connection=self.db_url,
        )

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", google_api_key=self.google_api_key
        )

    def search_documents(self, query: str) -> List[Tuple[Document, float]]:
        """Busca documentos similares."""
        return self.vectorstore.similarity_search_with_score(query, k=10)

    def build_context(self, documents: List[Tuple[Document, float]]) -> str:
        """Constrói contexto dos documentos."""
        return "\n".join([doc.page_content for doc, _ in documents])

    def answer(self, query: str) -> str:
        """Responde pergunta baseada no contexto."""
        if not query.strip():
            return "Por favor, faça uma pergunta válida."

        results = self.search_documents(query)
        context = self.build_context(results)

        PROMPT_TEMPLATE = """
        CONTEXTO:
        {contexto}

        REGRAS:
        - Responda somente com base no CONTEXTO.
        - Se a informação não estiver explicitamente no CONTEXTO, responda:
          "Não tenho informações necessárias para responder sua pergunta."
        - Nunca invente ou use conhecimento externo.
        - Nunca produza opiniões ou interpretações além do que está escrito.

        EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
        Pergunta: "Qual é a capital da França?"
        Resposta: "Não tenho informações necessárias para responder sua pergunta."

        Pergunta: "Quantos clientes temos em 2024?"
        Resposta: "Não tenho informações necessárias para responder sua pergunta."

        Pergunta: "Você acha isso bom ou ruim?"
        Resposta: "Não tenho informações necessárias para responder sua pergunta."

        PERGUNTA DO USUÁRIO:
        {pergunta}

        RESPONDA A "PERGUNTA DO USUÁRIO"
        """

        response = self.llm.invoke(
            PROMPT_TEMPLATE.format(contexto=context, pergunta=query)
        )
        return response.content
