# Description: skripta za postavljanje postavki modela i dodataka
import logging
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from config import LOG_LEVEL, OPENAI_API_KEY, SYSTEM_PROMPT 

def setup_logging():
    """
    Set up logging configuration.
    """
    logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logger


def setup_settings():
    """
    Sets up the settings for the model.
    """
    Settings.llm = OpenAI(
        model="gpt-4o-mini",  
        api_key=OPENAI_API_KEY,
        max_tokens=1000, 
        temperature=0.5,  #randomness of the model
        system_prompt=SYSTEM_PROMPT # Instructions for the model
    )
    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        chunk_size=800,
        chunk_overlap=300,
        api_key=OPENAI_API_KEY
    )

def is_pdf(filename):
    """
    Check if the filename represents a PDF file.
    """
    return filename.lower().endswith('.pdf')