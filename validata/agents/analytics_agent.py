"""Analytics Agent - orchestrates insight generation workflow"""
import logging
from typing import TypedDict, Optional, List
from uuid import UUID
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.models.analytics import Insight, Pattern

logger = logging.getLogger(__name__)


class AnalyticsState(TypedDict):
    """State for analytics workflow"""
    survey_id: UUID
    responses: List[dict]
    patterns: List[Pattern]
    insights: List[Insight]
    context: Optional[dict]
    error: Optional[str]


class AnalyticsAgent:
    """Orchestrates insight generation using LangGraph"""
    
    def __init__(self, analytics_mcp_client, memory_mcp_client):
        """
        Initialize agent
        
        Args:
            analytics_mcp_client: Client for Analytics MCP Server
            memory_mcp_client: Client for Memory MCP Server
        """
        self.analytics_client = analytics_mcp_client
        self.memory_client = memory_mcp_client
        self.checkpointer = MemorySaver()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the analytics workflow graph"""
        workflow = StateGraph(AnalyticsState)
        
        # Add nodes
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("detect_patterns", self._detect_patterns)
        workflow.add_node("generate_insights", self._generate_insights)
        workflow.add_node("store_insights", self._store_insights)
        workflow.add_node("handle_error", self._handle_error)
        
        # Set entry point
        workflow.set_entry_point("retrieve_context")
        
        # Add edges
        workflow.add_edge("retrieve_context", "detect_patterns")
        workflow.add_edge("detect_patterns", "generate_insights")
        workflow.add_edge("generate_insights", "store_insights")
        workflow.add_edge("store_insights", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _retrieve_context(self, state: AnalyticsState) -> AnalyticsState:
        """Retrieve account context from Memory MCP"""
        try:
            logger.info("Retrieving account context for analytics")
            
            # Get account_id from survey (would need to query survey first)
            # For now, we'll use a placeholder
            account_id = "default"
            
            request = {
                "tool": "get_account_context",
                "parameters": {
                    "account_id": account_id
                }
            }
            
            response = await self.memory_client.handle_request(request)
            
            if response["status"] == "success":
                state["context"] = response["data"]["context"]
                logger.info("Context retrieved successfully")
            else:
                logger.warning(f"Failed to retrieve context: {response['error']['message']}")
                state["context"] = {}
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            state["context"] = {}
        
        return state
    
    async def _detect_patterns(self, state: AnalyticsState) -> AnalyticsState:
        """Detect patterns in responses"""
        try:
            logger.info(f"Detecting patterns for survey {state['survey_id']}")
            
            request = {
                "tool": "detect_patterns",
                "parameters": {
                    "survey_id": str(state["survey_id"])
                }
            }
            
            response = await self.analytics_client.handle_request(request)
            
            if response["status"] == "success":
                patterns_data = response["data"]["patterns"]
                state["patterns"] = [Pattern(**p) for p in patterns_data]
                logger.info(f"Detected {len(state['patterns'])} patterns")
            else:
                state["error"] = response["error"]["message"]
                logger.error(f"Failed to detect patterns: {state['error']}")
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            state["error"] = str(e)
        
        return state
    
    async def _generate_insights(self, state: AnalyticsState) -> AnalyticsState:
        """Generate insights from patterns and responses"""
        try:
            logger.info(f"Generating insights for survey {state['survey_id']}")
            
            request = {
                "tool": "generate_insights",
                "parameters": {
                    "survey_id": str(state["survey_id"]),
                    "account_context": state.get("context")
                }
            }
            
            response = await self.analytics_client.handle_request(request)
            
            if response["status"] == "success":
                insights_data = response["data"]["insights"]
                state["insights"] = [Insight(**i) for i in insights_data]
                logger.info(f"Generated {len(state['insights'])} insights")
            else:
                state["error"] = response["error"]["message"]
                logger.error(f"Failed to generate insights: {state['error']}")
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            state["error"] = str(e)
        
        return state
    
    async def _store_insights(self, state: AnalyticsState) -> AnalyticsState:
        """Store insights in memory for future reference"""
        try:
            if not state.get("insights"):
                return state
            
            logger.info("Storing insights in memory")
            
            # Store summary of insights in memory
            insights_summary = f"Generated {len(state['insights'])} insights for survey {state['survey_id']}"
            
            # Would need account_id here
            account_id = "default"
            
            request = {
                "tool": "store_memory",
                "parameters": {
                    "account_id": account_id,
                    "content": insights_summary,
                    "metadata": {
                        "survey_id": str(state["survey_id"]),
                        "type": "analytics",
                        "insight_count": len(state["insights"])
                    }
                }
            }
            
            response = await self.memory_client.handle_request(request)
            
            if response["status"] == "success":
                logger.info("Insights stored in memory successfully")
            else:
                logger.warning(f"Failed to store insights in memory: {response['error']['message']}")
            
        except Exception as e:
            logger.error(f"Error storing insights: {e}")
        
        return state
    
    async def _handle_error(self, state: AnalyticsState) -> AnalyticsState:
        """Handle errors in analytics workflow"""
        logger.error(f"Analytics error: {state['error']}")
        return state
    
    async def generate_analytics(
        self,
        survey_id: UUID
    ) -> AnalyticsState:
        """
        Execute analytics workflow
        
        Args:
            survey_id: Survey UUID
        
        Returns:
            Final analytics state
        """
        initial_state = AnalyticsState(
            survey_id=survey_id,
            responses=[],
            patterns=[],
            insights=[],
            context=None,
            error=None
        )
        
        # Execute workflow
        config = {"configurable": {"thread_id": str(survey_id)}}
        final_state = await self.workflow.ainvoke(initial_state, config)
        
        return final_state
