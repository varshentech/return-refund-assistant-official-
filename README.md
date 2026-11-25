# Return and Refund Assistant

**Project ID:** PRJ-121  
**Category:** E-Commerce Customer Support  
**Project Type:** Academic Software Project

## 1. Project Overview

Return and Refund Assistant is a Python-based e-commerce customer support application designed to simplify order lookup, return request management, ticket tracking, and policy-related customer queries.

The application combines a Streamlit interface, SQLite database, and a Retrieval-Augmented Generation (RAG) architecture.

It uses **LangChain, Google Gemini Embeddings, ChromaDB, and Groq-hosted GPT-OSS 20B** to retrieve relevant policy information and generate natural-language answers to customer questions.

The project also includes greeting responses for common messages such as Hello, Hi, and Thank You.

## 2. Features

- **AI Policy Assistant:** Answers customer questions about return and refund policies using RAG and Generative AI.
- **Order Lookup:** Retrieves order information using order IDs.
- **Return Request Creation:** Validates return eligibility and creates return requests.
- **Ticket Tracking:** Allows customers to check the status of their return requests.
- **Admin Dashboard:** Displays application statistics and supports ticket status management.
- **Greeting Support:** Provides predefined responses to common greetings and thank-you messages.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development and backend logic |
| Streamlit | Builds the user interface |
| SQLite | Stores structured order and return-ticket records |
| LangChain | Connects and manages the AI workflow |
| RecursiveCharacterTextSplitter | Splits policy documents into smaller text chunks |
| Google Gemini Embeddings | Converts policy text and customer questions into numerical vectors |
| ChromaDB | Stores embeddings and retrieves relevant policy information |
| Groq API | Provides access to the language model for answer generation |
| GPT-OSS 20B | Generates natural-language answers using retrieved policy information |
| Python-dotenv | Loads API keys and configuration from the `.env` file |
| Git and GitHub | Version control and source-code hosting |

## 4. System Architecture

The application has two main workflows.

### A. Customer Management Workflow

1. The customer interacts with the Streamlit interface.
2. Python processes the requested operation.
3. SQLite retrieves or updates the relevant order and return-ticket records.
4. Streamlit displays the result to the customer or administrator.

**Important:** SQLite handles structured application data. It is separate from the AI policy retrieval system.

### B. AI Policy Assistant – RAG Workflow

The AI assistant uses Retrieval-Augmented Generation (RAG).

**Step 1 – Policy Document Preparation**

- Policy information is loaded from `policy.txt`.
- LangChain's `RecursiveCharacterTextSplitter` divides the document into smaller chunks.
- Google Gemini Embeddings converts each chunk into a numerical vector.
- ChromaDB stores the vectors along with their corresponding text.

**Step 2 – Customer Question Processing**

- The customer submits a policy-related question.
- Gemini Embeddings converts the question into a vector.
- LangChain sends the question vector to ChromaDB.
- ChromaDB performs similarity search and retrieves the most relevant policy chunks.

**Step 3 – AI Answer Generation**

- LangChain sends the customer's question and retrieved policy information to the Groq API.
- Groq runs the GPT-OSS 20B language model.
- The model generates a natural-language answer using the retrieved policy context.
- The application displays the generated answer to the customer.

### Understanding the Role of Each AI Component

| Component | What it actually does |
|---|---|
| LangChain | Coordinates the complete RAG workflow |
| Gemini Embeddings | Converts text into numerical vectors |
| ChromaDB | Stores and searches policy vectors |
| Groq API | Provides language-model inference |
| GPT-OSS 20B | Generates the final answer |

**Remember:** Gemini creates embeddings, ChromaDB retrieves information, LangChain connects the components, and GPT-OSS 20B generates the answer through Groq.

## 5. Project Architecture Diagram

```text
             CUSTOMER
                 |
                 v
          STREAMLIT UI
                 |
          PYTHON BACKEND
                 |
        +--------+---------+
        |                  |
        v                  v
   SQLITE DATABASE     AI POLICY ASSISTANT
        |                  |
        v                  v
  Orders and Tickets   LANGCHAIN
                           |
                    GEMINI EMBEDDINGS
                           |
                           v
                       CHROMADB
                           |
                    Retrieved Policy
                       Information
                           |
                           v
                       GROQ API
                           |
                      GPT-OSS 20B
                           |
                           v
                    GENERATED ANSWER
                           |
                           v
                     STREAMLIT UI
```

## 6. Project Folder Structure

```text
Return-Refund-Assistant/
|
|-- app.py
|-- rag_engine.py
|-- policy.txt
|-- requirements.txt
|-- README.md
|-- .gitignore
|
|-- chroma_db/          (Generated locally)
|-- return_refund.db    (Generated locally)
|-- screenshots/
|
|-- .env                (Local API keys - not uploaded)
```

**Important files:**

- `app.py`: Main Streamlit application containing the customer and admin modules.
- `rag_engine.py`: Handles embeddings, vector database operations, retrieval, and AI answer generation.
- `policy.txt`: Contains the return and refund policy information used by the AI assistant.
- `requirements.txt`: Lists the Python dependencies required to run the application.
- `.env`: Stores API keys locally. It must never be uploaded to GitHub.
- `chroma_db/`: Stores the locally persisted vector database.
- `return_refund.db`: Stores the application's SQLite data.

The SQLite database and ChromaDB directory are generated locally and excluded from the GitHub repository.

## 7. Installation and Setup

### Step 1 – Clone the repository

```bash
git clone https://github.com/varshentech/return-refund-assistant-official-.git
```

Navigate into the project directory:

```bash
cd return-refund-assistant-official-
```

### Step 2 – Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 3 – Configure API keys

Create a `.env` file in the project root directory.

Add the following configuration:

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
```

- Google API key: Used for Gemini Embeddings.
- Groq API key: Used for GPT-OSS 20B answer generation.

Never share API keys or upload the `.env` file to GitHub.

### Step 4 – Run the application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

## 8. Sample Order IDs

The application includes demonstration order records.

- ORD1001
- ORD1002
- ORD1003
- ORD1004
- ORD1005

These IDs can be used to test the Order Lookup functionality.

## 9. Current Limitations

- The application uses sample order and ticket data rather than a live e-commerce database.
- Actual payment gateway integration and automatic money transfers are not implemented.
- AI answer quality depends on the accuracy and completeness of the policy document.
- Common greeting responses are predefined rather than generated by the language model.
- The application is an academic demonstration and is not configured as a production-ready customer support service.
- The default demonstration admin password should be replaced with secure authentication before production deployment.

## 10. Future Enhancements

- Integration with a real e-commerce order management system.
- Secure administrator authentication and role-based access control.
- Automated refund processing through payment gateway integration.
- Improved AI response evaluation and policy-grounding validation.
- Customer conversation history and support analytics.
- Deployment to a cloud hosting platform.

## 11. Project Objective

The primary objective of this project is to combine conventional database-driven customer support operations with Generative AI and semantic information retrieval.

By integrating SQLite for structured data management and a RAG architecture for policy-related question answering, the application demonstrates how AI can improve the accessibility and efficiency of e-commerce customer support.

---

**Project:** Return and Refund Assistant  
**Project ID:** PRJ-121  
**Category:** E-Commerce Customer Support  
**Type:** Academic Software Project