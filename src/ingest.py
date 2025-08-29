import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from libs.envs.env_validator import validate_envs
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector


def ingest_pdf():
    load_dotenv()
    validate_envs()

    pdf_path = os.getenv("PDF_PATH", "document.pdf")
    db_url = os.getenv("DATABASE_URL")
    collection_name = os.getenv("PG_VECTOR_COLLECTION_NAME", "pdf_chunks")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", google_api_key=google_api_key
    )

    # Persistência no Postgres/pgVector
    vectorstore = PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        connection=db_url,
    )
    print(f"Ingestão concluída: {len(chunks)} chunks salvos em {collection_name}")


if __name__ == "__main__":
    ingest_pdf()
