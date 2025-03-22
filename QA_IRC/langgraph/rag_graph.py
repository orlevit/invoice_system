import os
import sys
from time import time
from typing import Any
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from IPython.display import Image, display

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(current_directory)
sys.path.append(parent_folder)

from config import *

# Define state
class State(TypedDict):
    vectorstore: Any
    question: str
    retrieved_docs: list
    answer: str
    formatted_context: str

# Function to remove non-ASCII characters
def remove_non_ascii(text):
    return ''.join([char for char in text if ord(char) < 128])

# Load and split documents
def load_and_split_document(documents_files_dir):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    documents = []
    for filename in os.listdir(documents_files_dir):
        file_path = os.path.join(documents_files_dir, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                content = remove_non_ascii(file.read())
                chunks = text_splitter.split_text(content)
                documents.extend([Document(page_content=chunk, metadata={"source": filename}) for chunk in chunks])
    return documents

# Create vectorstore
def create_vectorstore(documents_files_dir, persist_directory="chroma_db"):
    """
    Check if the vector store exists. If it does, load it.
    If not, process documents, create embeddings, and save the vector store.

    Returns: Chroma vector store instance
    """
    local_embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    # If vector store already exists, load and return it
    if os.path.exists(persist_directory):
        print("Loading existing vector store...")
        return Chroma(persist_directory=persist_directory, embedding_function=local_embeddings)

    # If vector store does not exist, process documents and create a new one
    print("Vector store not found. Processing documents and creating a new one...")
    all_splits = load_and_split_document(documents_files_dir)

    print("Creating new vector store...")
    tic = time()
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=local_embeddings, persist_directory=persist_directory)
    vectorstore.persist()  # Save the vector store for future use
    toc = time()
    print(f"Creating embedding took: {round((toc-tic)/60,2)} minutes")

    return vectorstore

# Retrieve documents
def retrieve_documents(state: State):
    retriever = state['vectorstore'].as_retriever()
    docs = retriever.invoke(state['question'])
    return {"retrieved_docs": docs}

# Format documents
def format_docs(state: State):
    return {"formatted_context": "\n\n".join(doc.page_content for doc in state['retrieved_docs'])}

# Generate answer
def generate_answer(state: State):
    model = ChatOllama(model=LLM_MODEL)
    rag_prompt = ChatPromptTemplate.from_template("""
        Answer the following question based only on the provided context:

        Context: {context}
        Question: {question}

        Answer:""")
    
    qa_chain = ({"context": RunnablePassthrough(), "question": RunnablePassthrough()} | rag_prompt | model | StrOutputParser())
    return {"answer": qa_chain.invoke({"context": state['formatted_context'], "question": state['question']})}

# Build workflow
workflow = StateGraph(State)
workflow.add_node("retrieve_documents", retrieve_documents)
workflow.add_node("format_docs", format_docs)
workflow.add_node("generate_answer", generate_answer)

workflow.add_edge(START, "retrieve_documents")
workflow.add_edge("retrieve_documents", "format_docs")
workflow.add_edge("format_docs", "generate_answer")
workflow.add_edge("generate_answer", END)

# Compile chain
chain = workflow.compile()

# Save the image
with open(os.path.join(GRAPH_IMAGES_DIR, 'rag.png'), "wb") as f:
    f.write(chain.get_graph().draw_mermaid_png())


# Create vectorstore
vectorstore = create_vectorstore(DOWNLOADED_DOCUMENTS, VECTORSTOR_DIR)

# Invoke workflow
question = "What is the Married Individuals Filing Joint Returns And Surviving Spouses table values?"
state = chain.invoke({"vectorstore": vectorstore, "question": question})

print("\nQuestion:", question)
print("\nQA Chain Response:", state["answer"])
