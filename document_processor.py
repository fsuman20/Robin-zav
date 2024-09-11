#=========1. START THE APP BY RUNNING document_processor.py================
#Description: skripta za ucitavanje i obradu dokumenata te stvaranje ili ucitavanje indeksa za pretrazivanje dokumenata
import os
from llama_parse import LlamaParse, ResultType
from llama_index.core import VectorStoreIndex, Document, StorageContext, load_index_from_storage, Settings
from llama_index.core.node_parser import MarkdownElementNodeParser
from config import INDEX_STORAGE_PATH, DOCUMENTS_PATH, set_openai_api_key
from model_utils import setup_logging, is_pdf, setup_settings

#OpenAI API key
set_openai_api_key()

logger = setup_logging()

# Initialize LlamaParse
llama_parser = LlamaParse(
    api_key="llx-zm8BN2XoR7RuvULERhiIWGgqIK65TBP0efuUciyS0EYelP7a",
    result_type=ResultType.MD,
    verbose=True
)

def load_documents():
    """
    Load and process PDF documents from a specified directory.
    Returns:
        list: A list of Document objects containing the text and extra information of each document.
    """
    documents = []
    for filename in os.listdir(DOCUMENTS_PATH):
        if is_pdf(filename):
            file_path = os.path.join(DOCUMENTS_PATH, filename)
            logger.info(f"Processing PDF: {filename}")
            try:
                with open(file_path, 'rb') as f:
                    parsed_docs = llama_parser.load_data(f, extra_info={"file_name": filename})
                
                for doc in parsed_docs:
                    documents.append(Document(text=doc.text, extra_info={"source": filename}))
                
                logger.info(f"Successfully processed {filename}")
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")
    return documents

def create_or_load_index():
    """
    Creates or loads an index for document processing.
    If an existing index is found in the specified storage path, it is loaded.
    Otherwise, a new index is created by loading documents, parsing them into nodes,
    and building a vector store index.
    Returns:
        index (VectorStoreIndex): The created or loaded index.
        None: If no valid PDF documents are found to index.
    """
    os.makedirs(INDEX_STORAGE_PATH, exist_ok=True)
    
    setup_settings()
    
    if os.path.exists(os.path.join(INDEX_STORAGE_PATH, "docstore.json")):
        logger.info("Loading existing index")
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE_PATH)
        index = load_index_from_storage(storage_context)
    else:    
        logger.info("Creating new index")
        documents = load_documents()
        if not documents:
            logger.warning("No PDF documents found to index")
            return None
        
        node_parser = MarkdownElementNodeParser(
            llm=Settings.llm,
            num_workers=8
        )
        
        nodes = node_parser.get_nodes_from_documents(documents)
        base_nodes, objects = node_parser.get_nodes_and_objects(nodes)
        
        index = VectorStoreIndex(nodes=base_nodes + objects)
        index.storage_context.persist(persist_dir=INDEX_STORAGE_PATH)
    
    return index

def query_index(index, query_text):
    """
    Queries the given index with the specified query text.
    Args:
        index: The index to query.
        query_text: The text of the query.
    Returns:
        A string representation of the query response, stripped of leading and trailing whitespace.
        Returns None if an error occurs during the query.
    """
    setup_settings()
    try:
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            verbose=True
        )
        
        response = query_engine.query(query_text)
        return str(response).strip()
        
    except Exception as e:
        logger.error(f"Error querying index: {str(e)}")
        return None

def process_documents():
    """
    Process documents and create or load an index.

    Returns:
        index (object): The created or loaded index.
    """
    logger.info("Pokretanje obrade dokumenata i indeksiranja...")
    index = create_or_load_index()
    if index:
        logger.info("Indeks uspješno stvoren ili učitan.")
        return index
    else:
        logger.warning("Indeks nije stvoren. Provjerite postoje li PDF datoteke u mapi documents.")
        return None

if __name__ == "__main__":
    index = process_documents()
    if index:
        test_queries = [
            "Što je FOI?",
            "Koji se studijski programi nude na FOI-u?",
            "Koliko traje preddiplomski studij na FOI-u?",
        ]
        for query in test_queries:
            response = query_index(index, query)
            logger.info(f"Test upit: {query}")
            logger.info(f"Odgovor: {response}\n")