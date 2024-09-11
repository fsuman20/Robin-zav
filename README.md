<div align="center">
    <img src="https://github.com/user-attachments/assets/f88e0969-109c-4e0a-9211-f9bf90d5467b" alt="Bez naslova (1500 x 1125 piks)" width="500"/>
</div>

# ROBIN - AI Asistent za Studente FOI-a

ROBIN (**ROB**otska **IN**teligencija) je chatbot sustav dizajniran za pružanje podrške studentima i osoblju Fakulteta organizacije i informatike (FOI). Ovaj projekt koristi velike jezične modele (LLM) i tehnike strojnog učenja za obradu prirodnog jezika (NLP), s ciljem pružanja točnih i relevantnih odgovora o fakultetskim programima, pravilnicima, kolegijima i resursima.

## Uvod

Ovaj projekt ima za cilj smanjiti opterećenje studentske referade pružanjem brzih odgovora na česta pitanja, poput informacija o kolegijima, pravilnicima i akademskom životu. Sustav koristi **Retrieval-Augmented Generation (RAG)** kako bi omogućio točne i kontekstualno relevantne odgovore.

## Struktura Projekta

Projekt je organiziran u nekoliko modula:

- **chat.py**: Glavni modul za upravljanje chatbotom i korisničkim interakcijama.
- **api.py**: Flask API za omogućavanje interakcije putem web sučelja i vanjskih aplikacija.
- **evaluation-metrics.py**: Modul za evaluaciju performansi modela na temelju točnosti, relevantnosti i koherentnosti odgovora.
- **model_utils.py**: Pomoćni alati za upravljanje i inicijalizaciju modela.
- **config.py**: Datoteka s postavkama projekta, uključujući API ključeve i konfiguracije modela.
- **document_processor.py**: Skripta za obradu i indeksiranje fakultetske dokumentacije.
- **demo.html**: Web sučelje za interakciju s chatbotom putem preglednika.

## Preduvjeti

Da biste pokrenuli ovaj projekt, potrebno je instalirati sljedeće Python pakete:

- `Flask`
- `llama-index`
- `openai`
- `numpy`
- `scikit-learn`
- `nltk`


## Instalacija

Klonirajte repozitorij te instalirajte potrebne biblioteke:
    ```bash
    git clone  https://github.com/fsuman20/Robin-zav.git
    ```

### Pokretanje Chatbota

Za pokretanje chatbota u interaktivnom načinu rada:

```bash
python chat.py
```

### Pokretanje API-ja

Pokretanje Flask API-ja za chatbot:

```bash
python api.py
```

API će biti dostupan na `http://127.0.0.1:5000`, a možete slati POST zahtjeve na `/query` s JSON tijelom koje sadrži `query`.

### Obrada dokumenata

Za pripremu dokumentacije koju chatbot koristi, pokrenite:

```bash
python document_processor.py
```

Ovo će stvoriti indeks za pretraživanje dokumenata.

## Evaluacija

Za procjenu performansi modela, koristite sljedeću naredbu:

```bash
python evaluation-metrics.py
```

Izvještaj će prikazati rezultate evaluacije, uključujući metrike poput BLEU score-a, relevantnosti i koherentnosti odgovora.

## Demo Web Sučelje

Za interakciju putem web preglednika, otvorite `demo.html`. Ovo sučelje koristi Flask API za omogućavanje korisnicima slanje upita putem preglednika.

## Prilagodba

ROBIN je lako prilagodljiv. Konfiguracije modela, uključujući **SYSTEM_PROMPT**, mogu se mijenjati unutar `config.py`. Dodatni dokumenti se mogu dodati u direktorij `storage`, nakon čega je potrebno izbrisati postojeće te ponovno pokrenuti `document_processor.py` kako bi se ažurirao indeks.

## Licenca

Projekt je licenciran pod [MIT licencom](LICENSE).


