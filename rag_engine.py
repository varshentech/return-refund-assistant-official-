
import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_chroma import Chroma


# Project paths
BASE_DIR = Path(__file__).resolve().parent
POLICY_FILE = BASE_DIR / "policy.txt"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "return_refund_policy"

load_dotenv(BASE_DIR / ".env")

# Cached components
_vector_store = None
_llm = None


def get_embeddings():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is missing. Check your .env file."
        )

    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=api_key
    )


def rebuild_vector_store():
    global _vector_store

    if not POLICY_FILE.exists():
        raise FileNotFoundError("policy.txt was not found.")

    if CHROMA_DIR.exists() and (CHROMA_DIR / "chroma.sqlite3").exists():
        shutil.rmtree(CHROMA_DIR)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    _vector_store = None

    policy_text = POLICY_FILE.read_text(encoding="utf-8")

    if not policy_text.strip():
        raise ValueError("policy.txt is empty.")

    document = Document(
        page_content=policy_text,
        metadata={"source": "policy.txt"}
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50
    )

    chunks = splitter.split_documents([document])
    embeddings = get_embeddings()

    _vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR)
    )

    return _vector_store


def get_vector_store():
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    if not POLICY_FILE.exists():
        raise FileNotFoundError("policy.txt was not found.")

    embeddings = get_embeddings()

    if (CHROMA_DIR / "chroma.sqlite3").exists():
        _vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DIR)
        )
    else:
        _vector_store = rebuild_vector_store()

    return _vector_store


def get_llm():
    global _llm

    if _llm is None:
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("Google API key is missing.")

        _llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            google_api_key=api_key
        )

    return _llm


def ask_policy(question):
    if not question or not question.strip():
        return {
            "answer": "Please enter a question.",
            "sources": []
        }

    vector_store = get_vector_store()

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 2}
    )

    documents = retriever.invoke(question)

    if not documents:
        return {
            "answer": (
                "I could not find relevant information "
                "in the return policy."
            ),
            "sources": []
        }

    context = "\n\n".join(
        doc.page_content for doc in documents
    )

    prompt = ChatPromptTemplate.from_template(
        """
        You are an e-commerce Return and Refund Assistant.

        Answer the customer's question using ONLY the
        policy context provided below.

        Rules:
        1. Do not invent return or refund rules.
        2. If the policy does not contain the answer,
           clearly say that the information is not available.
        3. Give clear and simple answers.
        4. Answer only what the customer asked.
        5. Keep the answer concise and relevant.
        6. Mention relevant conditions and time limits.

        POLICY CONTEXT:
        {context}

        CUSTOMER QUESTION:
        {question}
        """
    )

    chain = prompt | get_llm() | StrOutputParser()

    answer = chain.invoke({
        "context": context,
        "question": question
    })

    sources = list({
        doc.metadata.get("source", "policy.txt")
        for doc in documents
    })

    return {
        "answer": answer,
        "sources": sources
    }


def retrieve_policy(question):
    if not question or not question.strip():
        return {
            "answer": "Please enter a question.",
            "sources": []
        }

    vector_store = get_vector_store()

    documents = vector_store.similarity_search(
        question,
        k=2
    )

    if not documents:
        return {
            "answer": (
                "No relevant information found "
                "in the policy document."
            ),
            "sources": []
        }

    answer = "\n\n".join(
        doc.page_content for doc in documents
    )

    sources = list({
        doc.metadata.get("source", "policy.txt")
        for doc in documents
    })

    return {
        "answer": answer,
        "sources": sources
    }
