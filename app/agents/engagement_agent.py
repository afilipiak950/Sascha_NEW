from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
from langgraph.graph import StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor
from langchain_core.tools import tool
from app.services.linkedin_service import LinkedInService
from app.services.ai_service import AIService
from app.core.config import settings

logger = logging.getLogger(__name__)

class EngagementAgent:
    def __init__(self, linkedin_service: LinkedInService, ai_service: AIService):
        self.linkedin = linkedin_service
        self.ai = ai_service
        self.setup_tools()
        self.setup_graph()

    def setup_tools(self):
        """Definiert die Tools für den Engagement-Agenten"""
        @tool("find_relevant_posts")
        def find_relevant_posts(keywords: List[str], max_posts: int = 10) -> Dict:
            """Findet relevante Posts basierend auf Keywords."""
            try:
                posts = self.linkedin.search_posts(keywords, limit=max_posts)
                return {
                    "success": True,
                    "posts": posts,
                    "count": len(posts)
                }
            except Exception as e:
                logger.error(f"Fehler beim Suchen von Posts: {str(e)}")
                return {"success": False, "message": str(e)}

        @tool("analyze_post")
        def analyze_post(post_content: str) -> Dict:
            """Analysiert einen Post auf Interaktionspotenzial."""
            try:
                analysis = self.ai.analyze_post_engagement_potential(post_content)
                return {
                    "success": True,
                    "should_interact": analysis["should_interact"],
                    "reason": analysis["reason"],
                    "suggested_action": analysis["suggested_action"]
                }
            except Exception as e:
                logger.error(f"Fehler bei der Post-Analyse: {str(e)}")
                return {"success": False, "message": str(e)}

        @tool("generate_comment")
        def generate_comment(post_content: str, context: Dict) -> Dict:
            """Generiert einen relevanten Kommentar für einen Post."""
            try:
                comment = self.ai.generate_engagement_comment(
                    post_content=post_content,
                    post_context=context
                )
                return {
                    "success": True,
                    "comment": comment["text"],
                    "tone": comment["tone"],
                    "engagement_score": comment["engagement_score"]
                }
            except Exception as e:
                logger.error(f"Fehler bei der Kommentargenerierung: {str(e)}")
                return {"success": False, "message": str(e)}

        @tool("interact_with_post")
        def interact_with_post(post_url: str, action: str, comment_text: Optional[str] = None) -> Dict:
            """Führt eine Interaktion mit einem Post durch."""
            try:
                if action == "like":
                    success = self.linkedin.like_post(post_url)
                elif action == "comment" and comment_text:
                    success = self.linkedin.comment_on_post(post_url, comment_text)
                else:
                    return {"success": False, "message": "Ungültige Aktion"}

                return {
                    "success": success,
                    "action": action,
                    "message": f"{action} erfolgreich durchgeführt" if success else f"Fehler bei {action}"
                }
            except Exception as e:
                logger.error(f"Fehler bei der Post-Interaktion: {str(e)}")
                return {"success": False, "message": str(e)}

        self.tools = [find_relevant_posts, analyze_post, generate_comment, interact_with_post]

    def setup_graph(self):
        """Erstellt den Workflow-Graphen für den Engagement-Agenten"""
        # Tool-Executor erstellen
        self.executor = ToolExecutor(self.tools)

        # Graph-Knoten definieren
        def should_continue_engagement(state):
            """Prüft, ob weitere Interaktionen durchgeführt werden sollen"""
            if state.get("interaction_count", 0) >= settings.MAX_INTERACTIONS_PER_RUN:
                return "ende"
            if state.get("last_action", {}).get("success", False):
                return "weiter"
            return "ende"

        # Graph erstellen
        workflow = StateGraph(nodes=["find", "analyze", "engage"])
        
        # Kanten definieren
        workflow.add_edge("find", "analyze")
        workflow.add_edge("analyze", "engage")
        workflow.add_conditional_edges(
            "engage",
            should_continue_engagement,
            {
                "weiter": "find",
                "ende": END
            }
        )

        # Graph kompilieren
        self.graph = workflow.compile()

    async def run(self, keywords: List[str], max_interactions: int = 5) -> Dict:
        """Führt Engagement-Aktivitäten durch"""
        try:
            result = await self.graph.arun(
                {
                    "keywords": keywords,
                    "max_interactions": max_interactions,
                    "interaction_count": 0,
                    "start_time": datetime.now()
                }
            )
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Fehler bei der Ausführung des Engagement-Agenten: {str(e)}")
            return {"success": False, "error": str(e)} 