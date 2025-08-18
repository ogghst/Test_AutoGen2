# Sistema Multi-Agente per Documentazione di Progetto

## Scopo del Sistema

Il sistema implementa un framework multi-agente intelligente per l'automazione della creazione e gestione della documentazione di progetto software. Gli agenti collaborano per:

- **Automatizzare la creazione** di documentazione tecnica e organizzativa
- **Gestire il change management** con aggiornamenti automatici
- **Raccogliere requisiti** attraverso interazione intelligente
- **Generare piani di progetto** basati su best practices
- **Mantenere consistenza** tra documentazione e codice

## Architettura del Sistema

### Componenti Principali

```
┌─────────────────────────────────────────────────────┐
│                 Knowledge Base                      │
│                 (JSON-LD)                          │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│   │Methodologies│  │  Templates  │  │ Best        │ │
│   │(Agile,      │  │(Project     │  │ Practices   │ │
│   │Waterfall)   │  │Charter,PRD) │  │             │ │
│   └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│              Multi-Agent System                     │
│                                                     │
│  ┌─────────────┐    ┌─────────────┐                │
│  │ Project     │◄──►│Requirements │                │
│  │ Manager     │    │ Analyst     │                │
│  └─────────────┘    └─────────────┘                │
│         │                   │                      │
│         ▼                   ▼                      │
│  ┌─────────────┐    ┌─────────────┐                │
│  │ Change      │    │ Technical   │                │
│  │ Detector    │    │ Writer      │                │
│  └─────────────┘    └─────────────┘                │
│                                                     │
│         ▲                                           │
│         │ Ollama API (Local LLM)                   │
│         ▼                                           │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│               Document Store                        │
│              (File System)                         │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│   │Project      │  │Requirements │  │Technical    │ │
│   │Charter      │  │Documents    │  │Specs        │ │
│   └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Pattern Architetturali

- **Event-Driven Architecture**: Agenti reagiscono a eventi e messaggi
- **Microservices Pattern**: Ogni agente ha responsabilità specifiche
- **Repository Pattern**: Separazione tra logica business e persistenza dati
- **Strategy Pattern**: Metodologie intercambiabili (Agile, Waterfall)

## Tecnologie Utilizzate

### Core Framework
- **AutoGen**: Framework Microsoft per sistemi multi-agente
- **Ollama e Deepseek**: Due Large Language Models Utilizzabili
- **Python 3.12+**: Linguaggio di programmazione principale

### Modelli di Dati
- **JSON-LD**: Knowledge representation per entità e relazioni
- **Dataclasses**: Strutture dati tipizzate Python
- **Pydantic**: Validazione e serializzazione dati

### Persistenza
- **File System**: Storage documenti generati
- **JSON**: Indicizzazione e metadati
- **Markdown**: Formato output documenti

### Comunicazione
- **HTTP/REST**: Integrazione con Ollama API
- **Message Passing**: Comunicazione tra agenti
- **Async/Await**: Gestione operazioni asincrone

## Struttura dei File

```
project_management_system/      # python code root folder
│
├── models/
│   ├── __init__.py
│   └── data_models.py          # Dataclasses e enum
│
├── venv                        # python virtual environment
|
├── knowledge/
│   ├── __init__.py
│   ├── knowledge_base.py       # Gestione knowledge base JSON-LD
│   └── knowledge_base.jsonld   # KB con metodologie e template
│
├── storage/
│   ├── __init__.py
│   └── document_store.py       # Persistenza documenti output
│
├── agents/
│   ├── __init__.py            # Export agenti e factory function
│   ├── base_agent.py          # Classe base per agenti
│   ├── project_manager.py     # Agente orchestratore
│   ├── requirements_analyst.py # Agente raccolta requisiti
│   ├── change_detector.py     # Agente change management
│   └── technical_writer.py    # Agente documentazione tecnica
│
├── output_documents/          # Directory documenti generati
│   ├── document_index.json   # Indice documenti
│   └── [generated_docs].md   # Documenti markdown
│
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_knowledge_base.py
│   └── test_document_store.py
│
├── config/
│   ├── __init__.py
│   └── settings.py           # Configurazioni sistema
│
├── main.py                   # Demo e runner principale
├── requirements.txt          # Dipendenze Python
└── README.md                # Documentazione progetto
```

## Setup del Progetto

### Prerequisiti

1. **Python 3.12+** installato
2. **Ollama** installato e configurato
3. **Git** per cloning del progetto

### Step 1: Installazione Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Scarica installer da https://ollama.ai/download

# Avvia il servizio
ollama serve
```

### Step 2: Download Modello LLM

```bash
# Download modello consigliato (circa 2GB)
ollama pull llama3.2

# Verifica modelli disponibili
ollama list

# Test modello
ollama run llama3.2 "Hello, how are you?"
```

### Step 3: Configurazione LLM Provider

Il sistema può utilizzare due provider LLM: **DeepSeek** (cloud-based) o **Ollama** (local).

Crea un file `.env` nella root del progetto e imposta le seguenti variabili:

```env
# Scegli il provider: "deepseek" o "ollama"
LLM_PROVIDER=ollama

# --- Configurazione per DeepSeek (se LLM_PROVIDER="deepseek") ---
# DEEPSEEK_API_KEY=your_deepseek_api_key

# --- Configurazione per Ollama (se LLM_PROVIDER="ollama") ---
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

**Nota:** Assicurati di aver installato e avviato Ollama se lo selezioni come provider.

### Step 4: Setup Progetto Python

```bash
# Clona il progetto
git clone <repository_url>
cd project_management_system

# Crea virtual environment
python -m venv venv

# Attiva virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux  
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt
```

### Step 5: Contenuto requirements.txt

```txt
autogen-agentchat>=0.7.2
httpx>=0.24.0
asyncio-mqtt>=0.11.0
pydantic>=2.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
black>=23.0.0
isort>=5.12.0
mypy>=1.0.0
```

### Step 5: Configurazione Iniziale

```bash
# Crea directories necessarie
mkdir -p output_documents
mkdir -p knowledge
mkdir -p tests
mkdir -p config

# Imposta permessi (Linux/macOS)
chmod +x main.py
```

## Avvio del Sistema

### Step 1: Verifica Ollama

```bash
# Verifica che Ollama sia attivo
curl http://localhost:11434/api/tags

# Output atteso: lista dei modelli installati
```

### Step 2: Inizializzazione Knowledge Base

```bash
# Prima esecuzione - crea knowledge base
python -c "
from knowledge.knowledge_base import KnowledgeBase
kb = KnowledgeBase('knowledge_base.jsonld')
print('Knowledge Base initialized')
"
```

### Step 3: Avvio Demo Interattiva

```bash
# Avvia il sistema
python main.py
```

### Step 4: Comandi Demo

Una volta avviato il sistema, utilizza questi comandi:

```bash
# Inizializza progetto
init_project Progetto: E-commerce Platform, Obiettivi: Aumentare vendite online, Migliorare UX

# Verifica status
status

# Avvia raccolta requisiti
requirements

# Genera piano progetto
plan project

# Esci
quit
```

## Esempio di Utilizzo

```bash
👤 Your command: init_project Progetto: Sistema CRM, Obiettivi: Gestione clienti, Automazione vendite, Stakeholders: Team vendite, IT team

🤖 ProjectManager: ✅ PROJECT INITIALIZED: Sistema CRM

📋 Project ID: proj_20241201_143022
🎯 Objectives: Gestione clienti, Automazione vendite
👥 Stakeholders: Team vendite, IT team

📄 Project Charter generated and saved.

Next Steps:
1. Requirements gathering with RequirementsAnalyst
2. Detailed project planning
3. Resource allocation

Ready to proceed with requirements analysis.
```

## Testing

```bash
# Esegui test unit
pytest tests/

# Test specifico
pytest tests/test_agents.py -v

# Test con coverage
pytest --cov=agents tests/
```

## Implementazione Agenti

### Agenti Implementati

✅ **BaseProjectAgent**: Classe base con funzionalità comuni
✅ **ProjectManagerAgent**: Orchestrazione workflow e coordinamento progetto
✅ **RequirementsAnalystAgent**: Raccolta, analisi e validazione requisiti
✅ **ChangeDetectorAgent**: Monitoraggio cambiamenti e change management
✅ **TechnicalWriterAgent**: Generazione e gestione documentazione tecnica

### Caratteristiche Implementate

- **Pattern OOP**: Ogni agente ha responsabilità specifiche e ben definite
- **Async/Await**: Gestione asincrona per operazioni non bloccanti
- **DeepSeek Integration**: Utilizzo LLM per generazione contenuti intelligenti
- **Error Handling**: Gestione robusta degli errori con logging
- **Message Processing**: Sistema di routing messaggi per tipo di comando
- **Document Management**: Integrazione con storage e knowledge base

### Comandi Supportati

gli agenti possono dialogare con utente in modalità conversazionale, e traducono richieste utente in comandi:

#### Project Manager
- `init project` - Inizializzazione nuovo progetto
- `status` - Stato progetto corrente
- `requirements` - Avvio raccolta requisiti
- `plan project` - Pianificazione progetto

#### Requirements Analyst
- `gather requirements` - Raccolta requisiti da testo
- `analyze requirements` - Analisi requisiti raccolti
- `document requirements` - Creazione documentazione formale
- `interview questions` - Domande per interviste stakeholder
- `validate requirements` - Validazione qualità requisiti

#### Change Detector
- `monitor artifacts` - Configurazione monitoring
- `detect changes` - Rilevazione cambiamenti
- `analyze impact` - Analisi impatto cambiamenti
- `change history` - Cronologia cambiamenti
- `approve changes` - Gestione workflow approvazione
- `rollback changes` - Gestione rollback

#### Technical Writer
- `create document` - Creazione documenti tecnici
- `format document` - Applicazione formattazione
- `review document` - Revisione documenti
- `template management` - Gestione template
- `export document` - Esportazione formati diversi
- `organize documents` - Organizzazione documenti

## Estensioni Future

- **ZeroMQ**: Comunicazione inter-processo
- **Web Interface**: Dashboard di monitoraggio  
- **Database Integration**: PostgreSQL per persistenza
- **CI/CD Integration**: Automazione deployment
- **Metrics & Monitoring**: Osservabilità sistema

Il sistema fornisce una base solida e modulare per l'automazione della documentazione di progetto con capacità di estensione verso architetture distribuite. Tutti gli agenti sono stati implementati seguendo le best practices di programmazione orientata agli oggetti Python.
