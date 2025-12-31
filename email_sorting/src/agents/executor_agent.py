"""Executor Agent - Executes actions on emails"""

from typing import Dict, Any, List
from rich.console import Console

from ..graph.state import EmailState
from ..config import settings
from ..tools.gmail_tools import get_gmail_client

console = Console()


class ExecutorAgent:
    """Agent that executes actions on emails"""
    
    def __init__(self):
        self.provider = settings.EMAIL_PROVIDER
    
    def execute(self, state: EmailState) -> Dict[str, Any]:
        """
        Execute all actions in the state.
        
        Args:
            state: Current email state with actions to execute
        
        Returns:
            Updated state with execution results
        """
        actions = state.get("actions", [])
        message_id = state.get("message_id")
        
        if not actions:
            return {
                "processing_stage": "no_actions",
                "error": None
            }
        
        console.print(f"\n[cyan]Executing {len(actions)} actions on email {message_id}...[/cyan]")
        
        executed_actions = []
        failed_actions = []
        
        for action in actions:
            try:
                success = self._execute_action(message_id, action)
                if success:
                    executed_actions.append(action)
                    console.print(f"  [green]✓[/green] {action}")
                else:
                    failed_actions.append(action)
                    console.print(f"  [red]✗[/red] {action}")
            except Exception as e:
                failed_actions.append(action)
                console.print(f"  [red]✗[/red] {action}: {str(e)}")
        
        # Determine final status
        if failed_actions:
            error_msg = f"Failed actions: {', '.join(failed_actions)}"
            stage = "partially_executed"
        else:
            error_msg = None
            stage = "executed"
        
        return {
            "processing_stage": stage,
            "error": error_msg
        }
    
    def _execute_action(self, message_id: str, action: str) -> bool:
        """
        Execute a single action.
        
        Args:
            message_id: Email message ID
            action: Action string (e.g., "apply_label:work")
        
        Returns:
            True if successful
        """
        if self.provider == "gmail":
            return self._execute_gmail_action(message_id, action)
        elif self.provider == "outlook":
            return self._execute_outlook_action(message_id, action)
        elif self.provider == "imap":
            return self._execute_imap_action(message_id, action)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _execute_gmail_action(self, message_id: str, action: str) -> bool:
        """Execute action on Gmail"""
        client = get_gmail_client()
        
        # Parse action
        if action.startswith("apply_label:"):
            label_name = action.replace("apply_label:", "")
            return client.apply_label(message_id, label_name)
        
        elif action == "mark_important":
            return client.mark_as_important(message_id)
        
        elif action == "archive":
            return client.archive_message(message_id)
        
        elif action == "move_to_spam":
            return client.move_to_spam(message_id)
        
        elif action == "mark_as_read":
            return client.mark_as_read(message_id)
        
        elif action.startswith("move_to_folder:"):
            # Gmail uses labels instead of folders
            folder_name = action.replace("move_to_folder:", "")
            return client.apply_label(message_id, folder_name)
        
        elif action == "mark_for_followup":
            # Create a follow-up label
            return client.apply_label(message_id, "Follow-up")
        
        else:
            console.print(f"[yellow]Unknown action: {action}[/yellow]")
            return False
    
    def _execute_outlook_action(self, message_id: str, action: str) -> bool:
        """Execute action on Outlook (to be implemented)"""
        # TODO: Implement Outlook actions
        raise NotImplementedError("Outlook actions not yet implemented")
    
    def _execute_imap_action(self, message_id: str, action: str) -> bool:
        """Execute action on IMAP (to be implemented)"""
        # TODO: Implement IMAP actions
        raise NotImplementedError("IMAP actions not yet implemented")


# Node function for LangGraph
def executor_node(state: EmailState) -> Dict[str, Any]:
    """LangGraph node for action execution"""
    agent = ExecutorAgent()
    return agent.execute(state)
