#==============2. START THE APP BY RUNNING api.py================
# Description: Chatbot koji koristi prethodno trenirani model za odgovaranje na pitanja o sveučilištu.
from llama_index.core import StorageContext, load_index_from_storage
from config import INDEX_STORAGE_PATH, set_openai_api_key
from model_utils import setup_logging, setup_settings

# Set up logging and settings
logger = setup_logging()
set_openai_api_key()
setup_settings()

def initialize_index():
    """
    Initializes and returns an index by loading it from storage.
    """

    try:
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE_PATH) # ./storage
        index = load_index_from_storage(storage_context)
        logger.info("Index loaded successfully")
        return index
    except Exception as e:
        logger.error(f"Error loading index: {str(e)}")
        return None

def query_index(index, query_text):
    """
    Queries the given index with the specified query text.
    """
    query_engine = index.as_query_engine(
        similarity_top_k=5,
        verbose=True
    )
    response = query_engine.query(query_text)
    return str(response).strip()

def chat():
    """
    Initializes an index and starts a chat session with the user.
    """
    index = initialize_index()
    if index is None:
        print("Error pri pokretanju indexa. izlazim...")
        return

    print("\nDobrodošli! Ja sam Robin, AI asistent za pitanja o sveučilištu. Kako vam mogu pomoći? (Upišite 'exit' za izlaz)")
    while True:
        user_input = input("\nVi: ")
        if user_input.lower() == 'exit':
            print("Hvala na razgovoru. Doviđenja!")
            break
        
        response = query_index(index, user_input)
        if response is None:
            response = "Nažalost, nisam u mogućnosti odgovoriti na to pitanje. Molim vas, postavite drugo pitanje."
        print(response)

if __name__ == "__main__":
    chat()