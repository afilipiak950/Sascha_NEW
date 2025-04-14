from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.output_parsers import JsonOutputParser
from app.services.linkedin_service import LinkedInService
from app.services.ai_service import AIService
from app.core.config import settings

logger = logging.getLogger(__name__)

class LinkedInAgent:
    def __init__(self, linkedin_service: LinkedInService, ai_service: AIService):
        self.linkedin = linkedin_service
        self.ai = ai_service
        self.setup_tools()
        self.setup_graph()

    def setup_tools(self):
        """Definiert die Tools für den LinkedIn-Agenten"""
        @tool("create_post")
        def create_post(topic: str, tone: str = "professional", length: str = "medium") -> Dict:
            """Erstellt einen LinkedIn-Post zum angegebenen Thema."""
            try:
                content = self.ai.generate_post_content(topic, tone, length)
                success = self.linkedin.create_post(content)
                return {
                    "success": success,
                    "message": "Post erfolgreich erstellt" if success else "Fehler beim Erstellen des Posts"
                }
            except Exception as e:
                logger.error(f"Fehler beim Erstellen des Posts: {str(e)}")
                return {"success": False, "message": str(e)}

        @tool("engage_with_network")
        def engage_with_network(max_interactions: int = 5) -> Dict:
            """Interagiert mit dem LinkedIn-Netzwerk (Likes, Kommentare)."""
            try:
                interactions = 0
                for post in self.linkedin.get_feed_posts(limit=max_interactions):
                    if self.ai.should_interact_with_post(post["content"]):
                        if self.linkedin.like_post(post["url"]):
                            interactions += 1
                return {
                    "success": True,
                    "interactions": interactions,
                    "message": f"{interactions} Interaktionen durchgeführt"
                }
            except Exception as e:
                logger.error(f"Fehler bei Netzwerk-Interaktionen: {str(e)}")
                return {"success": False, "message": str(e)}

        @tool("analyze_engagement")
        def analyze_engagement() -> Dict:
            """Analysiert die Engagement-Metriken der letzten Posts."""
            try:
                metrics = self.linkedin.get_engagement_metrics()
                analysis = self.ai.analyze_engagement(metrics)
                return {
                    "success": True,
                    "analysis": analysis,
                    "metrics": metrics
                }
            except Exception as e:
                logger.error(f"Fehler bei der Engagement-Analyse: {str(e)}")
                return {"success": False, "message": str(e)}

        self.tools = [create_post, engage_with_network, analyze_engagement]

    def setup_graph(self):
        """Erstellt den Workflow-Graphen für den LinkedIn-Agenten"""
        # Tool-Executor erstellen
        self.executor = ToolExecutor(self.tools)

        # Prompt für den Agenten
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Du bist ein LinkedIn-Automatisierungsagent. Deine Aufgabe ist es, "
                      "das LinkedIn-Profil durch Posts und Interaktionen zu optimieren. "
                      "Nutze die verfügbaren Tools, um die bestmöglichen Ergebnisse zu erzielen."),
            MessagesPlaceholder(variable_name="messages"),
            ("human", "{input}"),
        ])

        # Graph-Knoten definieren
        def should_continue(state):
            """Entscheidet, ob weitere Aktionen notwendig sind"""
            messages = state["messages"]
            last_message = messages[-1]
            return "weiter" if "erfolgreich" in last_message.content.lower() else "ende"

        # Graph erstellen
        workflow = StateGraph(nodes=["agent", "tools"])
        
        # Kanten definieren
        workflow.add_edge("agent", "tools")
        workflow.add_conditional_edges(
            "tools",
            should_continue,
            {
                "weiter": "agent",
                "ende": END
            }
        )

        # Graph kompilieren
        self.graph = workflow.compile()

    async def run(self, task: str) -> Dict:
        """Führt eine Aufgabe mit dem LinkedIn-Agenten aus"""
        try:
            result = await self.graph.arun(
                {
                    "input": task,
                    "messages": []
                }
            )
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Fehler bei der Ausführung des Agenten: {str(e)}")
            return {"success": False, "error": str(e)} 