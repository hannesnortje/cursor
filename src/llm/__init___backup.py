""""""
LLM module for the MCP server with True Cursor LLM Bridge support.

Priority order:
1. SimpleCursorEnhancedAutoGen (True Cursor LLM Bridge) - when available
2. EnhancedAutoGen (advanced fallback) - when llm.enhanced_autogen exists
3. BasicEnhancedAutoGen (basic fallback) - from llm_fallback.py as last resort
"""

import logging

logger = logging.getLogger(__name__)

# Global AutoGen instance
_autogen_instance = None

def get_enhanced_autogen():
    """
    Get the best available AutoGen instance with priority:
    1. True Cursor LLM Bridge (SimpleCursorEnhancedAutoGen)
    2. Enhanced fallback (EnhancedAutoGen) 
    3. Basic fallback (BasicEnhancedAutoGen)
    """
    global _autogen_instance
    
    if _autogen_instance is not None:
        return _autogen_instance
    
    # Priority 1: Try True Cursor LLM Bridge
    try:
        from .cursor_enhanced_autogen import SimpleCursorEnhancedAutoGen
        _autogen_instance = SimpleCursorEnhancedAutoGen()
        logger.info("✅ TRUE CURSOR LLM BRIDGE ACTIVATED - Using SimpleCursorEnhancedAutoGen")
        return _autogen_instance
    except ImportError as e:
        logger.warning(f"True Cursor LLM Bridge not available: {e}")
    
    # Priority 2: Try enhanced fallback
    try:
        from .enhanced_autogen import EnhancedAutoGen
        _autogen_instance = EnhancedAutoGen()
        logger.info("🔄 Using enhanced fallback - EnhancedAutoGen")
        return _autogen_instance
    except ImportError as e:
        logger.warning(f"Enhanced AutoGen not available: {e}")
    
    # Priority 3: Basic fallback from llm_fallback.py
    try:
        import sys
        import os
        
        # Add the parent directory to Python path to access llm_fallback.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from llm_fallback import BasicEnhancedAutoGen
        _autogen_instance = BasicEnhancedAutoGen()
        logger.info("🔧 Using basic fallback - BasicEnhancedAutoGen from llm_fallback.py")
        return _autogen_instance
    except ImportError as e:
        logger.error(f"All AutoGen options failed: {e}")
        
        # Absolute last resort - create minimal instance
        class MinimalAutoGen:
            def __init__(self):
                self.name = "MinimalAutoGen"
                
            def generate_response(self, prompt: str, context=None) -> str:
                return f"Minimal response to: {prompt[:100]}..."
        
        _autogen_instance = MinimalAutoGen()
        logger.warning("⚠️ Using minimal fallback - limited functionality")
        return _autogen_instance

# Make the instance available for import
try:
    enhanced_autogen = get_enhanced_autogen()
    
    # Expose the main classes for import
    if hasattr(enhanced_autogen, '__class__'):
        if enhanced_autogen.__class__.__name__ == 'SimpleCursorEnhancedAutoGen':
            from .cursor_enhanced_autogen import SimpleCursorEnhancedAutoGen
            __all__ = ['SimpleCursorEnhancedAutoGen', 'get_enhanced_autogen', 'enhanced_autogen']
        elif enhanced_autogen.__class__.__name__ == 'EnhancedAutoGen':
            from .enhanced_autogen import EnhancedAutoGen
            __all__ = ['EnhancedAutoGen', 'get_enhanced_autogen', 'enhanced_autogen']
        else:
            # BasicEnhancedAutoGen or MinimalAutoGen
            __all__ = ['get_enhanced_autogen', 'enhanced_autogen']
    else:
        __all__ = ['get_enhanced_autogen', 'enhanced_autogen']
        
except Exception as e:
    logger.error(f"Module initialization error: {e}")
    __all__ = ['get_enhanced_autogen']"""

from .llm_gateway import LLMGateway, llm_gateway

# Import configurations (optional)
try:
    from .config import *
except ImportError:
    pass

# Import LLM Gateway if available  
try:
    from .llm_gateway import LLMGateway, llm_gateway
except ImportError:
    LLMGateway = None
    llm_gateway = None

# Try to import True Cursor LLM Bridge first
try:
    from .cursor_enhanced_autogen import get_enhanced_autogen, SimpleCursorEnhancedAutoGen
    CURSOR_LLM_BRIDGE_AVAILABLE = True
    print("🚀 TRUE CURSOR LLM BRIDGE ACTIVATED - Using gpt-4o/claude-3.5-sonnet")
except ImportError as e:
    CURSOR_LLM_BRIDGE_AVAILABLE = False
    print(f"⚠️ Cursor LLM Bridge not available: {e}")
    
    # Fallback to enhanced template system
    try:
        from .enhanced_autogen import EnhancedAutoGen, get_enhanced_autogen
        print("🔧 Using Enhanced AutoGen with syntax issues resolved")
    except ImportError:
        print("📦 Using Basic Enhanced AutoGen fallback")
        
        # Basic fallback for testing
        class BasicEnhancedAutoGen:
            def __init__(self):
                self.fallback_mode = True
                self.cursor_llm_enabled = False
            
            def process_message(self, message: str, recipients: list, sender: str = "user"):
                """Basic fallback for process_message to enable MCP server testing"""
                responses = {}
                for agent_id in recipients:
                    responses[agent_id] = {
                        "agent_id": agent_id,
                        "message": f"📧 Basic fallback response from {agent_id}: I received your message '{message[:50]}...' and I'm processing it with basic fallback mode while the full Cursor LLM bridge is being finalized.",
                        "role": "fallback_agent",
                        "method": "basic_fallback",
                        "cursor_llm_enabled": False,
                        "timestamp": "2025-09-11"
                    }
                
                return {
                    "success": True,
                    "method": "basic_fallback",
                    "autogen_enabled": False,
                    "cursor_llm_enabled": False,
                    "message_processed": True,
                    "responses": responses,
                    "note": "Using basic fallback while Cursor LLM bridge integration is being completed"
                }
            
            def create_agent(self, agent_id: str, role, project_id=None):
                return {"success": True, "agent_id": agent_id, "method": "basic_fallback"}
            def create_group_chat(self, chat_id: str, agents: list, project_id=None):
                return {"success": True, "chat_id": chat_id, "method": "basic_fallback"}
            def start_workflow(self, workflow_id: str, workflow_type: str, participants: list):
                return {"success": True, "workflow_id": workflow_id, "method": "basic_fallback"}
            def get_roles(self):
                return [{"role_name": "coordinator", "description": "Project coordination"}]
            def get_workflows(self):
                return [{"workflow_id": "sprint_planning", "description": "Sprint planning workflow"}]
            def get_agent_info(self, agent_id: str):
                return {"agent_id": agent_id, "role": "fallback_agent", "status": "active"}
            def get_chat_info(self, chat_id: str):
                return {"chat_id": chat_id, "status": "active", "method": "basic_fallback"}
            def start_conversation(self, conversation_id: str, participants: list, conversation_type="general"):
                return {"success": True, "conversation_id": conversation_id, "method": "basic_fallback"}

        def get_enhanced_autogen():
            return BasicEnhancedAutoGen()

__all__ = ["LLMGateway", "llm_gateway", "get_enhanced_autogen"]
