
import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq

from langchain_chroma import Chroma


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

POLICY_FILE = BASE_DIR / "policy.txt"
CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "return_refund_policy"

load_dotenv(BASE_DIR / ".env")

_vector_store = None
_llm = None


# --------------------------------------------------
# GOOGLE EMBEDDINGS
# --------------------------------------------------

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


# --------------------------------------------------
# CREATE / REBUILD CHROMADB
# --------------------------------------------------

def rebuild_vector_store():

    global _vector_store

    if not POLICY_FILE.exists():
        raise FileNotFoundError("policy.txt was not found.")

    if CHROMA_DIR.exists():
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


# --------------------------------------------------
# LOAD EXISTING CHROMADB
# --------------------------------------------------

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


# --------------------------------------------------
# GROQ LANGUAGE MODEL
# --------------------------------------------------

def get_llm():

    global _llm

    if _llm is None:

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is missing. Check your .env file."
            )

        model_name = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b"
        )

        _llm = ChatGroq(
            model=model_name,
            temperature=0.2,
            groq_api_key=api_key,
            max_retries=2,
            timeout=120
        )

    return _llm


# --------------------------------------------------
# CONVERSATIONAL RESPONSES
# --------------------------------------------------

def handle_conversation(question):

    message = question.strip().lower()
    message = message.strip("!.,? ")

    responses = {
        "hi": "Hello! Welcome to ShopEasy Support. How can I help you today?",
        "hello": "Hello! Welcome to ShopEasy Support. How can I assist you?",
        "hey": "Hey! Welcome to ShopEasy Support. What can I help you with?",
        "good morning": "Good morning! Welcome to ShopEasy Support. How can I help?",
        "good afternoon": "Good afternoon! How can I assist you today?",
        "good evening": "Good evening! Welcome to ShopEasy Support. How can I help?",
        "thanks": "You're welcome! Is there anything else I can help you with?",
        "thank you": "You're welcome! Thank you for choosing ShopEasy Support.",
        "bye": "Thank you for contacting ShopEasy Support. Have a nice day!",
        "goodbye": "Thank you for contacting ShopEasy Support. Have a nice day!"
    }

    if message in responses:

        return {
            "answer": responses[message],
            "sources": []
        }

    return None


# --------------------------------------------------
# AI POLICY ASSISTANT - RAG WORKFLOW
# --------------------------------------------------

def ask_policy(question):

    if not question or not question.strip():

        return {
            "answer": "Please enter a question.",
            "sources": []
        }

    # 1. Handle greetings and common conversation
    conversation_response = handle_conversation(question)

    if conversation_response is not None:
        return conversation_response

    try:

        # 2. Load ChromaDB
        vector_store = get_vector_store()

        # 3. Retrieve relevant policy information
        retriever = vector_store.as_retriever(
            search_kwargs={"k": 3}
        )

        documents = retriever.invoke(question)

        if not documents:

            return {
                "answer": (
                    "I could not find relevant information "
                    "in our return and refund policy. "
                    "Please contact customer support."
                ),
                "sources": []
            }

        # 4. Prepare retrieved context
        context = "\n\n".join(
            doc.page_content for doc in documents
        )

        # 5. Create LangChain prompt
        prompt = ChatPromptTemplate.from_template(
            """
            You are ShopEasy's professional
            Return and Refund Customer Support Assistant.

            Your job is to help customers understand
            return, refund, replacement and shipping policies.

            Follow these rules carefully:

            1. Answer using ONLY the policy context.
            2. Never invent policies or conditions.
            3. Answer directly and naturally.
            4. Use simple, customer-friendly language.
            5. Mention important deadlines and conditions.
            6. Avoid unnecessary repetition.
            7. If the policy does not contain the answer,
               clearly explain that the information
               is not available.
            8. Do not expose internal technical details.
            9. Do not repeat the entire policy document.
            10. Keep answers concise but informative.
            11. Be professional and polite.

            POLICY CONTEXT:
            {context}

            CUSTOMER QUESTION:
            {question}

            CUSTOMER SUPPORT ANSWER:
            """
        )

        # 6. Build LangChain processing chain
        chain = (
            prompt
            | get_llm()
            | StrOutputParser()
        )

        # 7. Generate AI response using Groq
        answer = chain.invoke({
            "context": context,
            "question": question
        })

        # 8. Collect source documents
        sources = list({
            doc.metadata.get("source", "policy.txt")
            for doc in documents
        })

        return {
            "answer": answer.strip(),
            "sources": sources
        }

    except Exception as error:

        print("AI POLICY ASSISTANT ERROR:", repr(error))

        raise RuntimeError(
            "Unable to generate an AI response. "
            "Please check the AI service connection "
            "and try again."
        ) from error


# --------------------------------------------------
# POLICY RETRIEVAL - WITHOUT AI GENERATION
# --------------------------------------------------

def retrieve_policy(question):

    if not question or not question.strip():

        return {
            "answer": "Please enter a question.",
            "sources": []
        }

    vector_store = get_vector_store()

    documents = vector_store.similarity_search(
        question,
        k=3
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
