# Return and Refund Assistant

**Project ID:** PRJ-121  
**Category:** E-Commerce Customer Support  
**Project Type:** Academic Software Project

## Overview

Return and Refund Assistant is a Python-based e-commerce customer support application designed to simplify order lookup, return request management, ticket tracking, and policy-related customer queries.

The application combines a Streamlit interface, SQLite database, and a Retrieval-Augmented Generation (RAG) architecture using LangChain and ChromaDB for semantic policy retrieval.

## Features

- **AI Policy Assistant:** Searches the return and refund policy document using semantic retrieval.
- **Order Lookup:** Retrieves order information using order IDs.
- **Return Request Creation:** Validates return eligibility and creates return requests.
- **Ticket Tracking:** Allows customers to check return request status.
- **Admin Dashboard:** Displays application statistics and supports ticket status management.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development and backend logic |
| Streamlit | User interface |
| SQLite | Structured order and ticket data storage |
| LangChain | AI workflow orchestration |
| ChromaDB | Vector storage and semantic retrieval |
| Google Gemini Embeddings | Text-to-vector conversion |
| Python-dotenv | Environment variable management |

## System Architecture

### Customer Management Workflow

1. Customer interacts with the Streamlit interface.
2. Python processes the requested operation.
3. SQLite retrieves or updates the relevant order and ticket records.
4. Streamlit displays the result.

### Policy Retrieval Workflow

1. Policy information is loaded from `policy.txt`.
2. LangChain splits the policy into smaller text chunks.
3. Gemini Embeddings converts the chunks into numerical vectors.
4. ChromaDB stores the vectors.
5. A customer submits a policy question.
6. The question is converted into a vector.
7. ChromaDB retrieves semantically relevant policy information.
8. The retrieved information is displayed in the application.

**Current implementation status:** Semantic policy retrieval is implemented. LLM-generated responses are a planned integration and are not yet available.

## Project Structure

```text
Return-Refund-Assistant/
│
├── app.py
├── rag_engine.py
├── policy.txt
├── requirements.txt
├── README.md
├── .gitignore
│
└── screenshots/
```

The ChromaDB database and SQLite database are generated locally and are not included in this repository.

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Return-Refund-Assistant
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure the API key

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
```

Never publish your API key or commit the `.env` file.

### 4. Run the application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal.

## Demo Information

Sample order IDs:

- ORD1001
- ORD1002
- ORD1003
- ORD1004
- ORD1005

This project uses demonstration data and is intended for academic purposes.

## Current Limitations

- LLM-generated policy responses are not yet integrated into the application.
- The policy assistant currently performs semantic retrieval rather than complete generative RAG.
- No real payment gateway or refund