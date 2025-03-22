# import required libraries
import os
from time import time
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import *




# Function to remove non-ASCII characters
def remove_non_ascii(text):
    return ''.join([char for char in text if ord(char) < 128])

def remove_non_ascii(text):
    """Removes non-ASCII characters from a string."""
    return ''.join([char for char in text if ord(char) < 128])

def load_and_split_document(documents_files_dir):
    """
    Reads all files in the directory, removes non-ASCII characters,
    splits them into chunks, and returns a list of Document objects.
    
    Returns:
        List[Document]: List of document chunks wrapped as `Document` objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP
    )

    documents = []  # Store `Document` objects

    # Loop through all files in the directory
    for filename in os.listdir(documents_files_dir):
        file_path = os.path.join(documents_files_dir, filename)

        # Check if it's a file
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                # Read the content of the file
                file_content = file.read()

                # Remove non-ASCII characters
                file_content = remove_non_ascii(file_content)

                # Split the content using RecursiveCharacterTextSplitter
                chunks = text_splitter.split_text(file_content)

                # Wrap each chunk in a Document object with metadata
                documents.extend([Document(page_content=chunk, metadata={"source": filename}) for chunk in chunks])

    return documents

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


def format_docs(docs):
    """
    Convert documents to string format
    Returns: Concatenated string of document contents
    """
    return "\n\n".join(doc.page_content for doc in docs)

def setup_qa_chain(vectorstore):
    """
    Set up an advanced QA chain with retrieval
    Returns: Callable QA chain
    """
    model = ChatOllama(model=LLM_MODEL)
    retriever = vectorstore.as_retriever()
    
    # Define RAG prompt template
    rag_prompt = ChatPromptTemplate.from_template(
        """Answer the following question based only on the provided context:

        Context: {context}
        Question: {question}

        Answer:"""
    )
    
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | rag_prompt
        | model
        | StrOutputParser()
    )

# Create or load the vector store
print("Creating vector store...")
vectorstore = create_vectorstore(DOWNLOADED_DOCUMENTS)

# Set up chains
print("Setting up chains...")
qa_chain = setup_qa_chain(vectorstore)

# Example usage
question = "What is the Married Individuals Filing Joint Returns And Surviving Spouses table values?"
print(f"\nQuestion: {question}")

# Get relevant documents
docs = vectorstore.similarity_search(question)

# # Get answer using QA chain
print("\nQA Chain Response:")
print(qa_chain.invoke(question))