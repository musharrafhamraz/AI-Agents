"""Survey Creator Agent - orchestrates AI-assisted survey creation"""
import logging
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.models.survey import Question, Survey

logger = logging.getLogger(__name__)


class SurveyCreationState(TypedDict):
    """State for survey creation workflow"""
    topic: str
    account_id: str
    context: Optional[dict]
    questions: List[Question]
    survey: Optional[Survey]
    error: Optional[str]


class SurveyCreatorAgent:
    """Orchestrates AI-assisted survey creation using LangGraph"""
    
    def __init__(self, survey_mcp_client, memory_mcp_client):
        """
        Initialize agent
        
        Args:
            survey_mcp_client: Client for Survey MCP Server
            memory_mcp_client: Client for Memory MCP Server
        """
        self.survey_client = survey_mcp_client
        self.memory_client = memory_mcp_client
        self.checkpointer = MemorySaver()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the survey creation workflow graph"""
        workflow = StateGraph(SurveyCreationState)
        
        # Add nodes
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("generate_questions", self._generate_questions)
        workflow.add_node("refine_questions", self._refine_questions)
        workflow.add_node("create_survey", self._create_survey)
        workflow.add_node("store_memory", self._store_memory)
        workflow.add_node("handle_error", self._handle_error)
        
        # Set entry point
        workflow.set_entry_point("retrieve_context")
        
        # Add edges
        workflow.add_edge("retrieve_context", "generate_questions")
        workflow.add_edge("generate_questions", "refine_questions")
        workflow.add_edge("refine_questions", "create_survey")
        workflow.add_edge("create_survey", "store_memory")
        workflow.add_edge("store_memory", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _retrieve_context(self, state: SurveyCreationState) -> SurveyCreationState:
        """Retrieve account context from Memory MCP"""
        try:
            logger.info(f"Retrieving context for account {state['account_id']}")
            
            request = {
                "tool": "get_account_context",
                "parameters": {
                    "account_id": state["account_id"]
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
    
    async def _generate_questions(self, state: SurveyCreationState) -> SurveyCreationState:
        """Generate initial questions using Survey MCP"""
        try:
            logger.info(f"Generating questions for topic: {state['topic']}")
            
            # For now, we'll create the survey directly which will generate questions
            # In a more complex workflow, we might generate questions separately first
            state["questions"] = []
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            state["error"] = str(e)
        
        return state
    
    async def _refine_questions(self, state: SurveyCreationState) -> SurveyCreationState:
        """Refine questions based on context"""
        try:
            logger.info("Refining questions based on context")
            
            # In a more sophisticated implementation, we might:
            # 1. Check questions against historical patterns
            # 2. Remove duplicate or similar questions
            # 3. Adjust question wording based on account preferences
            
            # For now, we'll proceed with generated questions
            
        except Exception as e:
            logger.error(f"Error refining questions: {e}")
            state["error"] = str(e)
        
        return state
    
    async def _create_survey(self, state: SurveyCreationState) -> SurveyCreationState:
        """Create survey in database"""
        try:
            logger.info("Creating survey")
            
            request = {
                "tool": "create_survey",
                "parameters": {
                    "topic": state["topic"],
                    "account_id": state["account_id"],
                    "account_context": state.get("context")
                }
            }
            
            response = await self.survey_client.handle_request(request)
            
            if response["status"] == "success":
                survey_data = response["data"]["survey"]
                state["survey"] = Survey(**survey_data)
                logger.info(f"Survey created: {state['survey'].id}")
            else:
                state["error"] = response["error"]["message"]
                logger.error(f"Failed to create survey: {state['error']}")
            
        except Exception as e:
            logger.error(f"Error creating survey: {e}")
            state["error"] = str(e)
        
        return state
    
    async def _store_memory(self, state: SurveyCreationState) -> SurveyCreationState:
        """Store survey creation in account memory"""
        try:
            if not state.get("survey"):
                return state
            
            logger.info("Storing survey creation in memory")
            
            memory_content = f"Created survey '{state['survey'].title}' about {state['topic']} with {len(state['survey'].questions)} questions"
            
            request = {
                "tool": "store_memory",
                "parameters": {
                    "account_id": state["account_id"],
                    "content": memory_content,
                    "metadata": {
                        "survey_id": str(state["survey"].id),
                        "topic": state["topic"],
                        "type": "survey_creation"
                    }
                }
            }
            
            response = await self.memory_client.handle_request(request)
            
            if response["status"] == "success":
                logger.info("Memory stored successfully")
            else:
                logger.warning(f"Failed to store memory: {response['error']['message']}")
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
        
        return state
    
    async def _handle_error(self, state: SurveyCreationState) -> SurveyCreationState:
        """Handle errors in survey creation"""
        logger.error(f"Survey creation error: {state['error']}")
        return state
    
    async def create_survey(
        self,
        topic: str,
        account_id: str
    ) -> SurveyCreationState:
        """
        Execute survey creation workflow
        
        Args:
            topic: Survey topic
            account_id: Account identifier
        
        Returns:
            Final survey creation state
        """
        initial_state = SurveyCreationState(
            topic=topic,
            account_id=account_id,
            context=None,
            questions=[],
            survey=None,
            error=None
        )
        
        # Execute workflow
        config = {"configurable": {"thread_id": f"{account_id}_{topic}"}}
        final_state = await self.workflow.ainvoke(initial_state, config)
        
        return final_state
