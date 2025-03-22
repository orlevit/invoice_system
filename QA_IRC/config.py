# Configuration
import os

# Directories
# Tax rules 
# START_P/ATTERN = r"פקודת מס הכנסה \[נוסח חדש\]\*\s*חלק א': פרשנות\s*"
# URL ="https://www.nevo.co.il/law_html/law01/255_001.htm"
RAG_BASE_DIR = 'QA_IRC'
SCRAP_DIR = 'scrap'
DOCUMENTS_DIR = 'sections'
CHROMA_DB_DIR = 'chroma_db'

# Vectorstore
VECTORSTOR_DIR = os.path.join(os.getcwd(), RAG_BASE_DIR, CHROMA_DB_DIR)

DOWNLOADED_DOCUMENTS = os.path.join(os.getcwd(), RAG_BASE_DIR, SCRAP_DIR, DOCUMENTS_DIR)

## LangGraph
LANGGRAPH_BASE_DIR = 'langgraph'
GRAPH_IMAGES_DIR = os.path.join(os.getcwd(), RAG_BASE_DIR, LANGGRAPH_BASE_DIR, 'images')

# Text splitting
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Model
EMBEDDING_MODEL = "all-minilm"#"nomic-embed-text"
LLM_MODEL = "qwen:0.5b"

