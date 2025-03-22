Implemention of a simple **Question Answering (QA) Retrieval-Augmented Generation (RAG)** system using **LangChain** and **LangGraph**. The QA system is designed to answer questions about the American **IRC (Internal Revenue Code)** using a **retrieval-based approach**.
This is suppose to be in Hebrew, however all the local models I tried of Ollama(less <= 7B parameters), yield nonsence output in Hebrew. So in the meanwhile, the American IRC is used.

## 📂 Project Structure
```
chroma_db/       # Vector database storage using ChromaDB
config.py        # Configuration file for model and database settings
langchain/       # Implementation of the QA system using LangChain
langgraph/       # Workflow implementation using LangGraph
scrap/           # Web scraping scripts for data collection
requirements.txt # Dependencies for the project
```

## 🚀 Getting Started
### 1️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 2️⃣ Run the QA System
```sh
python langchain/rag_cahin.py  # Run the LangChain-based QA system
python langgraph/rag_graph.py  # Run the LangGraph-based QA system
```
