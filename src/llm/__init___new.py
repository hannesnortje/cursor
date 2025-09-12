"""
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
    __all__ = ['get_enhanced_autogen']
