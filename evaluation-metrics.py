#description: skripta za evaluaciju chatbota koristeći različite metrike kao što su sličnost, koherencija i BLEU ocjena
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize
import nltk
from config import set_openai_api_key
from llama_index.core import StorageContext, load_index_from_storage, Settings
from config import INDEX_STORAGE_PATH
import warnings

nltk.download('punkt')
nltk.download('punkt_tab')

# Suppress NLTK warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Ensure OpenAI API key is set
set_openai_api_key()

# Download necessary NLTK data
nltk.download('punkt', quiet=True)

# Load index once
storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE_PATH)
index = load_index_from_storage(storage_context)

def calculate_relevance(query, response, reference_answer):
    """
    Calculate the relevance of the response to the query using cosine similarity.
    """
    # Get embeddings
    query_embedding = np.array(Settings.embed_model.get_query_embedding(query)).reshape(1, -1)
    response_embedding = np.array(Settings.embed_model.get_text_embedding(response)).reshape(1, -1)
    reference_embedding = np.array(Settings.embed_model.get_text_embedding(reference_answer)).reshape(1, -1)
    
    # Calculate cosine similarities
    query_response_similarity = cosine_similarity(query_embedding, response_embedding)[0][0]
    query_reference_similarity = cosine_similarity(query_embedding, reference_embedding)[0][0]
    
    # Calculate relevance score
    relevance_score = (query_response_similarity / query_reference_similarity) if query_reference_similarity != 0 else 0
    
    return min(relevance_score, 1.0)  # Cap the score at 1.0

def calculate_coherence(response):
    """
    Calculate the coherence of the response using a simple metric based on sentence structure.
    """
    sentences = response.split('.')
    if len(sentences) < 2:
        return 0.5  # Default score for very short responses
    
    # Check for common coherence indicators
    has_topic_sentence = any(len(sent.strip().split()) > 5 for sent in sentences[:2])
    has_connectives = any(word in response.lower() for word in ['however', 'therefore', 'because', 'additionally'])
    has_conclusion = len(sentences[-1].strip().split()) > 5
    
    coherence_score = (has_topic_sentence + has_connectives + has_conclusion) / 3
    return coherence_score

def calculate_bleu(response, reference_answer):
    """
    Calculate the BLEU score between the response and the reference answer.
    """
    response_tokens = word_tokenize(response.lower())
    reference_tokens = word_tokenize(reference_answer.lower())
    weights = (0.25, 0.25, 0.25, 0.25)  # Equal weights for 1-gram to 4-gram
    smoothing = SmoothingFunction().method1
    return sentence_bleu([reference_tokens], response_tokens, weights=weights, smoothing_function=smoothing)

def evaluate_response(query, response, reference_answer):
    """
    Evaluate the chatbot's response using multiple metrics.
    """
    relevance = calculate_relevance(query, response, reference_answer)
    coherence = calculate_coherence(response)
    bleu_score = calculate_bleu(response, reference_answer)
    
    # Calculate overall score (you can adjust the weights as needed)
    overall_score = 0.5 * np.array(relevance) + 0.3 * np.array(coherence) + 0.2 * np.array(bleu_score)
    
    return {
        'relevance': relevance,
        'coherence': coherence,
        'bleu_score': bleu_score,
        'overall_score': overall_score
    }

def run_evaluation(test_cases):
    """
    Run evaluation on a set of test cases.
    """
    scores = {
        'relevance': [],
        'coherence': [],
        'bleu_score': [],
        'overall_score': []
    }
    
    detailed_results = []
    
    for case in test_cases:
        query = case['query']
        reference_answer = case['reference_answer']
        
        response = str(index.as_query_engine().query(query))
        evaluation = evaluate_response(query, response, reference_answer)
        
        for metric, score in evaluation.items():
            scores[metric].append(score)
        
        detailed_results.append({
            'query': query,
            'chatbot_response': response,
            'reference_answer': reference_answer,
            'scores': evaluation
        })
    
    # Calculate average scores
    avg_scores = {metric: np.mean(score_list) for metric, score_list in scores.items()}
    
    return avg_scores, detailed_results

# Example usage
if __name__ == "__main__":
    from chat import query_index, initialize_index
    
    def chatbot(query):
        """
        A function that takes a query and returns the result from the index.
        """
        index = initialize_index()
        return query_index(index, query)
    
    test_cases = [
        {
            'query': "Što je FOI?",
            'reference_answer': "FOI je Fakultet organizacije i informatike, sastavnica Sveučilišta u Zagrebu."
        },
        {
            'query': "Koji se studijski programi nude na FOI-u?",
            'reference_answer': "FOI nudi preddiplomske studije Informacijski i poslovni sustavi (IPS) te Informacijske tehnologije i digitalizaciju poslovanja (ITDP)."
        },
        {
            'query': "Koje predmete treba položiti na Državnoj maturi za upis na studij Informacijski i poslovni sustavi?",
            'reference_answer': "Predmeti koje treba položiti su Hrvatski jezik, Matematika (A), i Informatika (nije obavezna, ali nosi 15% bodova)."
        },
        {
            'query': "Da li se predmeti upisuju odjednom za prvi i drugi semestar na FOI-ju?",
            'reference_answer': "Ne, predmeti se upisuju posebno za svaki semestar. U srpnju se biraju predmeti za prvi semestar, a u veljači za drugi semestar."
        },
        {
            'query': "Što se događa ako student ne uspije položiti ispit u godini dana?",
            'reference_answer': "Ako student ne uspije položiti ispit u godini dana, mora ponovno upisati predmet te sudjelovati u kontinuiranom praćenju."
        },
        {
            'query': "Koliko puta student može prijaviti ispit u istoj akademskoj godini?",
            'reference_answer': "Student može polagati ispit iz istog predmeta najviše četiri puta u istoj akademskoj godini."
        },
        {
            'query': "Koja je procedura za prijavu teme završnog rada na preddiplomskim studijima na FOI-ju?",
            'reference_answer': "Student može prijaviti temu završnog rada nakon upisa predmeta \"Završni rad\", a najkasnije do kraja 6. tjedna ljetnog semestra. Prijava se vrši putem sustava FOI-radovi."
        },
        {
            'query': "Što se događa ako student ne obrani završni/diplomski rad u roku od dvije godine?",
            'reference_answer': "Student mora izabrati i upisati novu temu završnog/diplomskog rada."
        },
        {
            'query': "Koji su obavezni strani jezici na prvoj godini studija na FOI-ju?",
            'reference_answer': "Na prvoj godini studija potrebno je upisati jedan strani jezik po želji, engleski ili njemački, ovisno o dosadašnjem obrazovanju."
        },
        {
            'query': "Je li predmet Tjelesna i zdravstvena kultura obavezan na FOI-ju?",
            'reference_answer': "Da, predmet Tjelesna i zdravstvena kultura je obavezan za sve redovne studente na prvoj i drugoj godini studija, ali ga izvanredni studenti ne upisuju."
        },
        {
            'query': "Kako se na FOI-ju evidentiraju ocjene studenata?",
            'reference_answer': "Ocjene studenata na FOI-ju se evidentiraju isključivo putem sustava ISVU, od akademske godine 2018./2019., dok je korištenje indeksa ukinuto."
        },
        {
            'query': "Koliko se puta smije prijaviti ispit iz istog predmeta na FOI-ju?",
            'reference_answer': "Ispit iz istog predmeta može se polagati najviše četiri puta u istoj akademskoj godini, a ukupno najviše osam puta."
        },
        {
            'query': "Kada student može prijaviti temu završnog rada na preddiplomskom studiju?",
            'reference_answer': "Student može prijaviti temu završnog rada nakon upisa predmeta \"Završni rad\", a najkasnije do kraja 6. tjedna ljetnog semestra."
        },
        {
            'query': "Što se događa ako student ne obrani završni rad unutar dvije godine od prihvaćanja teme?",
            'reference_answer': "Ako student ne obrani završni rad unutar dvije godine, mora izabrati i upisati novu temu završnog rada."
        },
        {
            'query': "Mogu li se ocjene ostvariti putem kolokvija na FOI-ju?",
            'reference_answer': "Da, ocjene se najčešće ostvaruju putem kolokvija koji se odnose na određenu cjelinu gradiva predmeta."
        },
        {
            'query': "Koliko tema završnog rada treba ponuditi svaki potencijalni mentor na FOI-ju?",
            'reference_answer': "Svaki potencijalni mentor na FOI-ju dužan je studentima omogućiti izbor najmanje pet tema završnog rada po studijskom programu."
        },
        {
            'query': "Kako se može prijaviti i obraniti završni rad na stranom jeziku na FOI-ju?",
            'reference_answer': "Završni rad se može prijaviti i obraniti na stranom jeziku uz pisanu zamolbu studenta i suglasnost mentora, koju odobrava prodekan za nastavu."
        },
        {
            'query': "Što se događa ako student dobije negativnu ocjenu na obrani završnog rada?",
            'reference_answer': "Ako student dobije negativnu ocjenu, mora izabrati i prijaviti novu temu završnog rada. Postupak prijave nove teme nakon negativne ocjene može se provesti samo jednom."
        }
    ]
    
    avg_scores, detailed_results = run_evaluation(test_cases)
    
    print("Average Evaluation Scores:")
    for metric, score in avg_scores.items():
        print(f"{metric}: {score:.4f}")
    
    print("\nDetailed Results:")
    for i, result in enumerate(detailed_results, 1):
        print(f"\nTest Case {i}:")
        print(f"Query: {result['query']}")
        print(f"Chatbot Response: {result['chatbot_response']}")
        print(f"Reference Answer: {result['reference_answer']}")
        print("Scores:")
        for metric, score in result['scores'].items():
            print(f"  {metric}: {score:.4f}")