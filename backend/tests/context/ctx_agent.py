
"""
PromptToGraphRoutedAgent - Agente AutoGen per trasformazione di prompt in grafi

Implementa l'architettura proposta per il controllo del contesto e del flusso
in agenti LLM multi-tool, con focus sulla manipolazione di grafi.

Caratteristiche principali:
- Progressive Context Disclosure
- Tool auto-descrittivi con intelligence degli errori
- Escalation intelligente dei fallimenti
- Gestione controllata del contesto

Autore: Implementazione basata sui principi architetturali del paper
        "Controllo del Contesto e del Flusso in Agenti LLM Multi-Tool"
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import json
import asyncio
import re
import uuid

# Per integrazione con AutoGen reale, decommentare:
# from autogen_core import RoutedAgent, MessageContext, message_handler

# STRUTTURE DATI PER IL SISTEMA DI MESSAGGI
@dataclass
class PromptToGraphRequest:
    """Richiesta per convertire un prompt in struttura a grafo"""
    prompt: str
    context: Optional[str] = None
    graph_type: str = "knowledge_graph"  # knowledge_graph, workflow_graph, concept_map
    max_nodes: int = 50
    max_depth: int = 3
    include_relationships: bool = True

@dataclass 
class GraphNode:
    """Nodo del grafo"""
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    position: Optional[Dict[str, float]] = None

@dataclass
class GraphEdge:
    """Arco del grafo"""
    id: str
    source: str
    target: str
    relationship: str
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GraphStructure:
    """Struttura completa del grafo"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "nodes": [
                {
                    "id": node.id,
                    "label": node.label,
                    "type": node.type,
                    "properties": node.properties,
                    "position": node.position
                } for node in self.nodes
            ],
            "edges": [
                {
                    "id": edge.id,
                    "source": edge.source,
                    "target": edge.target,
                    "relationship": edge.relationship,
                    "weight": edge.weight,
                    "properties": edge.properties
                } for edge in self.edges
            ],
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        """Esporta il grafo in formato JSON"""
        return json.dumps(self.to_dict(), indent=2)

    def export_to_cypher(self) -> str:
        """Esporta il grafo come script Cypher per Neo4j"""
        cypher_commands = []

        # Crea nodi
        for node in self.nodes:
            props = {**node.properties, "label": node.label}
            props_str = ", ".join([f"{k}: '{v}'" for k, v in props.items()])
            cypher_commands.append(f"CREATE (:{node.type} {{{props_str}}})")

        # Crea relazioni
        for edge in self.edges:
            source_label = next((n.label for n in self.nodes if n.id == edge.source), edge.source)
            target_label = next((n.label for n in self.nodes if n.id == edge.target), edge.target)
            cypher_commands.append(
                f"MATCH (a {{label: '{source_label}'}}), (b {{label: '{target_label}'}}) "
                f"CREATE (a)-[:{edge.relationship.upper().replace(' ', '_')}]->(b)"
            )

        return "\n".join(cypher_commands)

@dataclass
class PromptToGraphResponse:
    """Risposta con il grafo generato"""
    graph: GraphStructure
    processing_info: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None

# CLASSI DI SUPPORTO
@dataclass
class ExecutionStep:
    name: str
    description: str

@dataclass
class ExecutionPlan:
    steps: List[ExecutionStep]
    context_id: str

@dataclass
class StepResult:
    success: bool
    data: Any = None
    error: Optional[str] = None

# CONTEXT MANAGER - Implementa Progressive Context Disclosure
class GraphContextManager:
    """
    Gestore del contesto per agenti LLM multi-tool.
    Implementa i principi di controllo del contesto e progressive disclosure.
    """

    def __init__(self):
        self.contexts = {}

    def create_context(self, original_prompt: str, request_params: PromptToGraphRequest, objective: str) -> str:
        """Crea un nuovo contesto di esecuzione"""
        context_id = str(uuid.uuid4())

        self.contexts[context_id] = {
            "objective": objective,
            "original_prompt": original_prompt,
            "request_params": request_params,
            "current_step": 0,
            "steps_completed": [],
            "failures": [],
            "extracted_entities": [],
            "identified_relationships": [],
            "graph_structure": None,
            "metadata": {}
        }

        return context_id

    def prepare_minimal_context(self, context_id: str) -> Dict[str, Any]:
        """Prepara il contesto minimo per l'LLM - Principio di progressive disclosure"""
        context = self.contexts[context_id]

        return {
            "objective": context["objective"],
            "current_prompt": context["original_prompt"],
            "current_step": context["current_step"],
            "graph_type": context["request_params"].graph_type,
            "max_nodes": context["request_params"].max_nodes
        }

    def add_error_context(self, llm_context: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """Aggiunge contesto di errore per il recovery"""
        context = self.contexts[context_id]

        if context["failures"]:
            last_failure = context["failures"][-1]
            llm_context["last_error"] = last_failure
            llm_context["error_guidance"] = self._generate_error_guidance(last_failure)

        return llm_context

    def add_historical_context(self, llm_context: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """Aggiunge contesto storico per fallimenti ripetuti"""
        context = self.contexts[context_id]

        llm_context["completed_steps"] = context["steps_completed"]
        llm_context["all_failures"] = context["failures"]
        llm_context["extracted_entities"] = context["extracted_entities"]
        llm_context["identified_relationships"] = context["identified_relationships"]

        return llm_context

    def update_with_result(self, context_id: str, result: StepResult):
        """Aggiorna il contesto con i risultati dello step"""
        context = self.contexts[context_id]

        if result.success:
            step_name = self._get_current_step_name(context["current_step"])
            context["steps_completed"].append({
                "step": step_name,
                "result": result.data
            })

            # Aggiorna dati specifici basati sul tipo di step
            if step_name == "extract_entities":
                context["extracted_entities"] = result.data
            elif step_name == "identify_relationships":
                context["identified_relationships"] = result.data
            elif step_name == "construct_graph":
                context["graph_structure"] = result.data

    def record_failure(self, context_id: str, error: str):
        """Registra un fallimento per la diagnostica"""
        context = self.contexts[context_id]
        import datetime
        context["failures"].append({
            "step": context["current_step"],
            "error": error,
            "timestamp": datetime.datetime.now().isoformat()
        })

    def advance_step(self, context_id: str):
        """Avanza al prossimo step dell'esecuzione"""
        self.contexts[context_id]["current_step"] += 1

    def is_complete(self, context_id: str) -> bool:
        """Verifica se l'esecuzione Ã¨ completata"""
        context = self.contexts[context_id]
        return context["current_step"] >= 5  # 5 steps totali

    def get_current_step(self, context_id: str) -> str:
        """Ottiene il nome dello step corrente"""
        step_index = self.contexts[context_id]["current_step"]
        return self._get_current_step_name(step_index)

    def get_final_result(self, context_id: str) -> GraphStructure:
        """Costruisce il risultato finale del grafo"""
        context = self.contexts[context_id]

        if context["graph_structure"]:
            return context["graph_structure"]

        # Fallback: costruisci un grafo semplice dalle entitÃ  estratte
        return self._build_fallback_graph(context)

    def _get_current_step_name(self, step_index: int) -> str:
        steps = ["analyze_prompt", "extract_entities", "identify_relationships", "construct_graph", "optimize_layout"]
        return steps[step_index] if step_index < len(steps) else "complete"

    def _generate_error_guidance(self, failure: Dict[str, Any]) -> str:
        """Genera guidance per il recovery da errori"""
        return f"Errore nello step {failure['step']}: {failure['error']}. Prova un approccio diverso."

    def _build_fallback_graph(self, context: Dict[str, Any]) -> GraphStructure:
        """Costruisce un grafo di fallback da entitÃ  estratte"""
        nodes = []
        edges = []

        # Crea nodi dalle entitÃ  estratte
        for i, entity in enumerate(context.get("extracted_entities", [])):
            nodes.append(GraphNode(
                id=f"node_{i}",
                label=entity.get("name", f"Entity_{i}"),
                type=entity.get("type", "concept")
            ))

        # Crea edges dalle relazioni
        for i, rel in enumerate(context.get("identified_relationships", [])):
            edges.append(GraphEdge(
                id=f"edge_{i}",
                source=rel.get("source", "node_0"),
                target=rel.get("target", "node_1"),
                relationship=rel.get("type", "related_to")
            ))

        return GraphStructure(
            nodes=nodes,
            edges=edges,
            metadata={
                "source": "fallback_construction",
                "original_prompt": context["original_prompt"]
            }
        )

# GRAPH TOOLS - Implementano Tool Auto-Descrittivi
class GraphTools:
    """
    Strumenti intelligenti per la manipolazione di grafi.
    Implementano interfacce conversazionali che restituiscono errori comprensibili.
    """

    def __init__(self):
        self.entity_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Proper nouns
            r'\b\w+(?:ing|tion|ment|ness|ity)\b',   # Common noun endings
        ]
        self.relationship_keywords = [
            "is", "has", "contains", "causes", "leads to", "relates to", 
            "depends on", "influences", "creates", "belongs to", "includes"
        ]

    async def analyze_prompt(self, prompt: str, context: Dict[str, Any]) -> StepResult:
        """
        Analizza il prompt per identificare struttura e intento.
        Restituisce errori comprensibili invece di codici tecnici.
        """
        try:
            if not prompt or len(prompt.strip()) < 10:
                return StepResult(
                    success=False,
                    error="Il prompt Ã¨ troppo corto. Fornisci almeno 10 caratteri di testo significativo per l'analisi."
                )

            analysis = {
                "prompt_length": len(prompt),
                "word_count": len(prompt.split()),
                "complexity": self._assess_complexity(prompt),
                "main_topics": self._extract_main_topics(prompt),
                "graph_hints": self._identify_graph_structure_hints(prompt)
            }

            return StepResult(success=True, data=analysis)

        except Exception as e:
            return StepResult(
                success=False,
                error=f"Errore nell'analisi del prompt: {str(e)}. Verifica che il testo sia in un formato leggibile."
            )

    async def extract_entities(self, prompt: str, context: Dict[str, Any]) -> StepResult:
        """Estrae entitÃ  dal prompt con gestione intelligente degli errori"""
        try:
            entities = []
            words = prompt.split()

            # Estrazione entitÃ  basata su pattern
            for i, word in enumerate(words):
                if word.istitle() and len(word) > 2:  # Possibile nome proprio
                    entities.append({
                        "name": word,
                        "type": "proper_noun",
                        "position": i,
                        "context": " ".join(words[max(0, i-2):i+3])
                    })

            # Estrazione concetti chiave
            concepts = self._extract_concepts(prompt)
            for concept in concepts:
                entities.append({
                    "name": concept,
                    "type": "concept",
                    "context": prompt
                })

            if len(entities) == 0:
                return StepResult(
                    success=False,
                    error="Non sono riuscito a identificare entitÃ  significative nel testo. Prova con un prompt che contenga nomi, concetti o termini specifici."
                )

            # Limita il numero di entitÃ  secondo i parametri
            max_nodes = context.get("max_nodes", 50)
            if len(entities) > max_nodes:
                entities = entities[:max_nodes]

            return StepResult(success=True, data=entities)

        except Exception as e:
            return StepResult(
                success=False,
                error=f"Errore nell'estrazione delle entitÃ : {str(e)}. Il testo potrebbe contenere caratteri non supportati."
            )

    async def identify_relationships(self, entities: List[Dict], prompt: str, context: Dict[str, Any]) -> StepResult:
        """Identifica relazioni tra entitÃ  con feedback intelligente"""
        try:
            if not entities or len(entities) < 2:
                return StepResult(
                    success=False,
                    error="Servono almeno 2 entitÃ  per identificare relazioni. L'estrazione di entitÃ  precedente potrebbe non aver funzionato correttamente."
                )

            relationships = []

            # Analisi co-occorrenza e prossimitÃ  nel testo
            for i, entity1 in enumerate(entities):
                for j, entity2 in enumerate(entities[i+1:], i+1):
                    relationship = self._analyze_relationship(entity1, entity2, prompt)
                    if relationship:
                        relationships.append(relationship)

            # Analisi pattern linguistici
            linguistic_rels = self._extract_linguistic_relationships(prompt, entities)
            relationships.extend(linguistic_rels)

            if len(relationships) == 0:
                return StepResult(
                    success=False,
                    error="Non ho trovato relazioni chiare tra le entitÃ . Il testo potrebbe essere troppo frammentato o le entitÃ  troppo distanti concettualmente."
                )

            return StepResult(success=True, data=relationships)

        except Exception as e:
            return StepResult(
                success=False,
                error=f"Errore nell'identificazione delle relazioni: {str(e)}. Le entitÃ  fornite potrebbero avere un formato non valido."
            )

    async def construct_graph(self, entities: List[Dict], relationships: List[Dict], context: Dict[str, Any]) -> StepResult:
        """Costruisce la struttura del grafo con validazione intelligente"""
        try:
            nodes = []
            edges = []

            # Creazione nodi
            for i, entity in enumerate(entities):
                if not entity.get("name"):
                    continue  # Salta entitÃ  senza nome

                node = GraphNode(
                    id=f"node_{i}",
                    label=entity["name"],
                    type=entity.get("type", "unknown"),
                    properties={
                        "context": entity.get("context", ""),
                        "position_in_text": entity.get("position", -1)
                    }
                )
                nodes.append(node)

            # Creazione archi
            node_map = {node.label: node.id for node in nodes}

            for i, rel in enumerate(relationships):
                source_name = rel.get("source")
                target_name = rel.get("target")

                source_id = node_map.get(source_name)
                target_id = node_map.get(target_name)

                if source_id and target_id and source_id != target_id:
                    edge = GraphEdge(
                        id=f"edge_{i}",
                        source=source_id,
                        target=target_id,
                        relationship=rel.get("type", "related_to"),
                        weight=rel.get("strength", 1.0)
                    )
                    edges.append(edge)

            if len(nodes) == 0:
                return StepResult(
                    success=False,
                    error="Non Ã¨ stato possibile creare nodi validi. Verifica che le entitÃ  abbiano nomi definiti."
                )

            graph = GraphStructure(
                nodes=nodes,
                edges=edges,
                metadata={
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "graph_density": len(edges) / (len(nodes) * (len(nodes) - 1) / 2) if len(nodes) > 1 else 0,
                    "processing_timestamp": str(uuid.uuid4())
                }
            )

            return StepResult(success=True, data=graph)

        except Exception as e:
            return StepResult(
                success=False,
                error=f"Errore nella costruzione del grafo: {str(e)}. I dati di entitÃ  o relazioni potrebbero essere corrotti."
            )

    def _assess_complexity(self, prompt: str) -> str:
        """Valuta la complessitÃ  del prompt"""
        word_count = len(prompt.split())
        if word_count < 20:
            return "low"
        elif word_count < 100:
            return "medium"
        else:
            return "high"

    def _extract_main_topics(self, prompt: str) -> List[str]:
        """Estrae i topic principali del prompt"""
        words = prompt.lower().split()
        topics = [word for word in words if len(word) > 6 and word.isalpha()]
        return topics[:5]  # Top 5

    def _identify_graph_structure_hints(self, prompt: str) -> List[str]:
        """Identifica suggerimenti per la struttura del grafo"""
        hints = []

        structure_keywords = {
            "hierarchy": ["hierarchy", "level", "above", "below", "parent", "child"],
            "network": ["network", "connected", "link", "relationship", "between"],
            "flow": ["flow", "process", "step", "sequence", "then", "after"],
            "cluster": ["group", "category", "type", "kind", "similar"]
        }

        prompt_lower = prompt.lower()
        for structure_type, keywords in structure_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                hints.append(structure_type)

        return hints

    def _extract_concepts(self, prompt: str) -> List[str]:
        """Estrae concetti chiave dal prompt"""
        # Pattern per sostantivi composti e termini tecnici
        patterns = [
            r'\b[a-z]+(?:ing|tion|ment|ness|ity)\b',  # Sostantivi derivati
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',   # Nomi propri
        ]

        concepts = []
        for pattern in patterns:
            matches = re.findall(pattern, prompt)
            concepts.extend(matches)

        # Rimuovi duplicati e parole troppo c
