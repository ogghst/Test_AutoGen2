# PromptToGraphRoutedAgent - Agente AutoGen per Trasformazione Prompt-to-Graph

## Panoramica

Questo progetto implementa un agente AutoGen di tipo `RoutedAgent` che trasforma prompt in strutture di oggetti a grafo, seguendo l'architettura proposta nel paper "Controllo del Contesto e del Flusso in Agenti LLM Multi-Tool: Un Approccio Architetturale per la Manipolazione di Grafi".

## Caratteristiche Principali

### ðŸŽ¯ Architettura Controllata
- **Progressive Context Disclosure**: Gestione controllata del contesto fornito all'LLM
- **Escalation Intelligente**: Gestione robusta dei fallimenti con diagnostica automatica
- **Tool Auto-Descrittivi**: Interfacce conversazionali che restituiscono errori comprensibili

### ðŸ”§ FunzionalitÃ  Tecniche
- Estrazione automatica di entitÃ  da testo non strutturato
- Identificazione di relazioni semantiche tra entitÃ 
- Costruzione di grafi strutturati con metadati
- Esportazione in formato JSON e Cypher (Neo4j)
- Gestione intelligente degli errori con recovery automatico

### ðŸ“Š Tipi di Grafi Supportati
- **Knowledge Graph**: Grafi di conoscenza da testo narrativo
- **Workflow Graph**: Grafi di processo e flussi di lavoro
- **Concept Map**: Mappe concettuali e relazioni cognitive

## Installazione e Setup

### Prerequisiti
```bash
pip install autogen-core
pip install asyncio
```

### File Richiesti
- `prompt_to_graph_routed_agent.py` - Implementazione principale
- `README-agent.md` - Questa documentazione

## Utilizzo Base

### 1. Creazione dell'Agente
```python
from prompt_to_graph_routed_agent import PromptToGraphRoutedAgent, PromptToGraphRequest
from autogen_core import MessageContext

# Inizializzazione
agent = PromptToGraphRoutedAgent()
```

### 2. Configurazione della Richiesta
```python
request = PromptToGraphRequest(
    prompt="""
    Il machine learning Ã¨ una branca dell'intelligenza artificiale che utilizza algoritmi 
    per imparare dai dati. I neural networks sono un tipo di algoritmo di machine learning 
    che imita il cervello umano.
    """,
    graph_type="knowledge_graph",
    max_nodes=20,
    max_depth=3,
    include_relationships=True
)
```

### 3. Esecuzione della Trasformazione
```python
ctx = MessageContext(topic_id="example")
response = await agent.handle_prompt_to_graph_request(request, ctx)

if response.success:
    print(f"Grafo generato: {len(response.graph.nodes)} nodi, {len(response.graph.edges)} archi")
    
    # Esportazione
    json_graph = response.graph.to_json()
    cypher_script = response.graph.export_to_cypher()
else:
    print(f"Errore: {response.error_message}")
```

## Integrazione con AutoGen Runtime

### Setup Completo
```python
from autogen_core import SingleThreadedAgentRuntime, AgentId
from prompt_to_graph_routed_agent import PromptToGraphRoutedAgent, PromptToGraphRequest

async def setup_autogen_system():
    # Creazione runtime
    runtime = SingleThreadedAgentRuntime()
    
    # Registrazione agente
    await PromptToGraphRoutedAgent.register(
        runtime, 
        "prompt_to_graph_agent",
        lambda: PromptToGraphRoutedAgent()
    )
    
    runtime.start()
    
    # Utilizzo
    agent_id = AgentId("prompt_to_graph_agent", "default")
    request = PromptToGraphRequest(prompt="Your prompt here...")
    
    response = await runtime.send_message(request, agent_id)
    
    await runtime.stop()
    return response
```

## Architettura del Sistema

### Componenti Principali

1. **PromptToGraphRoutedAgent**: Agente principale con gestione dei messaggi
2. **GraphContextManager**: Gestione del contesto e progressive disclosure
3. **GraphTools**: Strumenti intelligenti per manipolazione grafi
4. **Strutture Dati**: `GraphNode`, `GraphEdge`, `GraphStructure`

### Flusso di Esecuzione

1. **Analisi Prompt**: Identificazione di struttura e complessitÃ 
2. **Estrazione EntitÃ **: Riconoscimento di nomi, concetti e termini chiave
3. **Identificazione Relazioni**: Analisi di co-occorrenze e pattern linguistici
4. **Costruzione Grafo**: Assemblaggio della struttura finale
5. **Ottimizzazione Layout**: Preparazione per visualizzazione

### Progressive Context Disclosure

```python
# Tentativo 1: Contesto minimo
llm_context = {
    "objective": "Transform prompt into graph",
    "current_prompt": prompt,
    "current_step": 0
}

# Tentativo 2: + Contesto di errore
llm_context.update({
    "last_error": "Error details...",
    "error_guidance": "Try different approach..."
})

# Tentativo 3: + Contesto storico completo
llm_context.update({
    "completed_steps": [...],
    "all_failures": [...],
    "extracted_entities": [...]
})
```

## Esempi Avanzati

### Grafo di Processo Aziendale
```python
request = PromptToGraphRequest(
    prompt="""
    Il processo di onboarding inizia con la registrazione del nuovo dipendente.
    Segue la fase di formazione che include training sulla sicurezza e corsi specifici.
    Dopo la formazione, il dipendente viene assegnato a un team e riceve gli strumenti di lavoro.
    """,
    graph_type="workflow_graph",
    max_nodes=15
)
```

### Mappa Concettuale
```python
request = PromptToGraphRequest(
    prompt="""
    La sostenibilitÃ  ambientale comprende tre pilastri: ambientale, sociale ed economico.
    L'economia circolare Ã¨ un modello che minimizza gli sprechi massimizzando il riutilizzo.
    Le energie rinnovabili includono solare, eolico, idroelettrico e geotermico.
    """,
    graph_type="concept_map",
    max_nodes=25,
    include_relationships=True
)
```

## Gestione degli Errori

### Tipi di Errore Gestiti
- **Prompt Insufficiente**: "Il prompt Ã¨ troppo corto. Fornisci almeno 10 caratteri..."
- **EntitÃ  Non Trovate**: "Non sono riuscito a identificare entitÃ  significative..."
- **Relazioni Mancanti**: "Non ho trovato relazioni chiare tra le entitÃ ..."
- **Costruzione Fallita**: "Non Ã¨ stato possibile creare nodi validi..."

### Escalation Intelligente
- **Tentativo 1**: Esecuzione standard con contesto minimo
- **Tentativo 2**: Aggiunta di guidance specifica per l'errore
- **Tentativo 3**: Contesto storico completo per recovery avanzato
- **Fallimento Finale**: Escalation all'utente con diagnostica completa

## Esportazione e Integrazione

### Formato JSON
```json
{
  "nodes": [
    {
      "id": "node_0",
      "label": "Machine Learning",
      "type": "concept",
      "properties": {
        "context": "branch of artificial intelligence"
      }
    }
  ],
  "edges": [
    {
      "id": "edge_0", 
      "source": "node_0",
      "target": "node_1",
      "relationship": "is_a",
      "weight": 1.5
    }
  ],
  "metadata": {
    "total_nodes": 10,
    "total_edges": 8,
    "graph_density": 0.18
  }
}
```

### Script Cypher per Neo4j
```cypher
CREATE (:concept {label: 'Machine Learning', context: 'branch of artificial intelligence'})
CREATE (:concept {label: 'Neural Networks', context: 'type of algorithm'})
MATCH (a {label: 'Machine Learning'}), (b {label: 'Neural Networks'}) 
CREATE (a)-[:INCLUDES]->(b)
```

## Performance e ScalabilitÃ 

### Limiti Configurabili
- **max_nodes**: Numero massimo di nodi nel grafo (default: 50)
- **max_depth**: ProfonditÃ  massima delle relazioni (default: 3)
- **max_attempts**: Tentativi massimi per step (default: 3)

### Ottimizzazioni
- Chunking automatico per prompt lunghi
- Deduplicazione entitÃ 
- Pruning delle relazioni deboli
- Caching dei risultati intermedi

## Estensioni Future

### FunzionalitÃ  Pianificate
- [ ] Integrazione con modelli LLM specifici
- [ ] Supporto per grafi temporali
- [ ] Visualizzazione interattiva
- [ ] Clustering automatico di entitÃ  simili
- [ ] Validazione semantica delle relazioni

### Plugin e Integrazioni
- Neo4j Database Connector
- NetworkX Compatibility
- D3.js Visualization
- Gephi Export Format

## Troubleshooting

### Problemi Comuni
1. **Importazione fallita**: Verificare che `autogen-core` sia installato
2. **Grafo vuoto**: Prompt troppo generico, aggiungere dettagli specifici
3. **Troppe entitÃ **: Ridurre `max_nodes` o migliorare il filtering
4. **Relazioni assenti**: Prompt troppo frammentato, aggiungere connettori

### Debug
```python
# Abilita logging dettagliato
import logging
logging.basicConfig(level=logging.DEBUG)

# Ispeziona il contesto
context_id = response.processing_info['context_id']
agent.context_manager.contexts[context_id]
```

## Riferimenti e Licenza

### Paper di Riferimento
"Controllo del Contesto e del Flusso in Agenti LLM Multi-Tool: Un Approccio Architetturale per la Manipolazione di Grafi"

### Framework Utilizzati
- Microsoft AutoGen Framework
- Python asyncio
- Regular Expressions per NLP
- UUID per identificatori unici

### Licenza
MIT License - Libero per uso commerciale e non commerciale

---

**Sviluppato per l'ecosistema AutoGen - Implementazione di riferimento per agenti controllati di trasformazione prompt-to-graph**
