"""Database schemas for the vector database."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum


class DocumentType(Enum):
    """Document type enumeration."""
    CODE_CONTEXT = "code_context"
    CONVERSATION = "conversation"
    DOCUMENTATION = "documentation"
    PROJECT_STATE = "project_state"
    GIT_OPERATION = "git_operation"
    CURSOR_SESSION = "cursor_session"
    AGENT_COLLABORATION = "agent_collaboration"
    AGILE_PROJECT = "agile_project"
    DOCUMENTATION_ARTIFACT = "documentation_artifact"


class CodeLanguage(Enum):
    """Programming language enumeration."""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SCALA = "scala"
    R = "r"
    MATLAB = "matlab"
    OTHER = "other"


@dataclass
class CodeContext:
    """Code context for vector database storage."""
    id: str
    file_path: str
    function_name: Optional[str] = None
    code_snippet: str = ""
    ast_representation: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    language: CodeLanguage = CodeLanguage.PYTHON
    framework: Optional[str] = None
    complexity_score: float = 0.0
    last_modified: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "file_path": self.file_path,
            "function_name": self.function_name,
            "code_snippet": self.code_snippet,
            "ast_representation": self.ast_representation,
            "dependencies": self.dependencies,
            "language": self.language.value,
            "framework": self.framework,
            "complexity_score": self.complexity_score,
            "last_modified": self.last_modified.isoformat(),
            "metadata": self.metadata,
            "embedding": self.embedding
        }


@dataclass
class Conversation:
    """Conversation data for vector database storage."""
    id: str
    agent_id: str
    user_id: str
    message: str
    response: str
    context: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    task_type: str = "general"
    confidence_score: float = 0.0
    llm_used: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "message": self.message,
            "response": self.response,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "task_type": self.task_type,
            "confidence_score": self.confidence_score,
            "llm_used": self.llm_used,
            "metadata": self.metadata,
            "embedding": self.embedding
        }


@dataclass
class Documentation:
    """Documentation data for vector database storage."""
    id: str
    title: str
    content: str
    doc_type: str = "general"
    related_files: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_by: str = ""
    last_updated: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    status: str = "draft"
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "doc_type": self.doc_type,
            "related_files": self.related_files,
            "tags": self.tags,
            "created_by": self.created_by,
            "last_updated": self.last_updated.isoformat(),
            "version": self.version,
            "status": self.status,
            "metadata": self.metadata,
            "embedding": self.embedding
        }


@dataclass
class ProjectState:
    """Project state data for vector database storage."""
    id: str
    project_name: str
    current_tasks: List[Dict[str, Any]] = field(default_factory=list)
    active_agents: List[str] = field(default_factory=list)
    system_status: str = "idle"
    recent_changes: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "project_name": self.project_name,
            "current_tasks": self.current_tasks,
            "active_agents": self.active_agents,
            "system_status": self.system_status,
            "recent_changes": self.recent_changes,
            "performance_metrics": self.performance_metrics,
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class GitOperation:
    """Git operation data for vector database storage."""
    id: str
    operation_type: str
    agent_id: str
    files_changed: List[str] = field(default_factory=list)
    commit_message: Optional[str] = None
    branch_name: Optional[str] = None
    merge_strategy: Optional[str] = None
    status: str = "pending"
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""
    repository: str = ""
    conflicts: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "operation_type": self.operation_type,
            "agent_id": self.agent_id,
            "files_changed": self.files_changed,
            "commit_message": self.commit_message,
            "branch_name": self.branch_name,
            "merge_strategy": self.merge_strategy,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "repository": self.repository,
            "conflicts": self.conflicts,
            "performance_metrics": self.performance_metrics,
            "metadata": self.metadata,
            "embedding": self.embedding
        }


@dataclass
class CursorSession:
    """Cursor session data for vector database storage."""
    session_id: str
    project_path: str
    active_agents: List[str] = field(default_factory=list)
    chat_sessions: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)
    agent_status: Dict[str, str] = field(default_factory=dict)
    llm_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "session_id": self.session_id,
            "project_path": self.project_path,
            "active_agents": self.active_agents,
            "chat_sessions": self.chat_sessions,
            "last_activity": self.last_activity.isoformat(),
            "agent_status": self.agent_status,
            "llm_context": self.llm_context,
            "metadata": self.metadata
        }


@dataclass
class AgentCollaboration:
    """Agent collaboration data for vector database storage."""
    id: str
    collaboration_id: str
    participating_agents: List[str] = field(default_factory=list)
    shared_context: List[str] = field(default_factory=list)
    collaboration_type: str = "general"
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "collaboration_id": self.collaboration_id,
            "participating_agents": self.participating_agents,
            "shared_context": self.shared_context,
            "collaboration_type": self.collaboration_type,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata,
            "embedding": self.embedding
        }


@dataclass
class AgileProject:
    """Agile project data for vector database storage."""
    id: str
    project_name: str
    sprint_number: int = 1
    sprint_duration: int = 14
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    user_stories: List[Dict[str, Any]] = field(default_factory=list)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    velocity: float = 0.0
    burndown_data: List[Dict[str, Any]] = field(default_factory=list)
    team_members: List[str] = field(default_factory=list)
    status: str = "planning"
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "project_name": self.project_name,
            "sprint_number": self.sprint_number,
            "sprint_duration": self.sprint_duration,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "user_stories": self.user_stories,
            "tasks": self.tasks,
            "velocity": self.velocity,
            "burndown_data": self.burndown_data,
            "team_members": self.team_members,
            "status": self.status,
            "metadata": self.metadata,
            "embedding": self.embedding
        }


@dataclass
class DocumentationArtifact:
    """Documentation artifact data for vector database storage."""
    id: str
    title: str
    content: str
    doc_type: str = "general"
    related_files: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    status: str = "draft"
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "doc_type": self.doc_type,
            "related_files": self.related_files,
            "tags": self.tags,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "version": self.version,
            "status": self.status,
            "metadata": self.metadata,
            "embedding": self.embedding
        }


# Collection configuration for Qdrant
COLLECTION_CONFIGS = {
    "code_context": {
        "vector_size": 1536,
        "distance": "Cosine",
        "description": "Code context and snippets"
    },
    "conversations": {
        "vector_size": 1536,
        "distance": "Cosine",
        "description": "Agent conversations and interactions"
    },
    "documentation": {
        "vector_size": 1536,
        "distance": "Cosine",
        "description": "Project documentation and guides"
    },
    "project_state": {
        "vector_size": 512,
        "distance": "Cosine",
        "description": "Project state and metadata"
    },
    "git_operations": {
        "vector_size": 512,
        "distance": "Cosine",
        "description": "Git operations and history"
    },
    "cursor_sessions": {
        "vector_size": 512,
        "distance": "Cosine",
        "description": "Cursor IDE session data"
    },
    "agent_collaboration": {
        "vector_size": 1024,
        "distance": "Cosine",
        "description": "Agent collaboration context"
    },
    "agile_projects": {
        "vector_size": 1024,
        "distance": "Cosine",
        "description": "Agile project management data"
    },
    "documentation_artifacts": {
        "vector_size": 1536,
        "distance": "Cosine",
        "description": "Documentation artifacts and versions"
    }
}


def get_collection_config(collection_name: str) -> Dict[str, Any]:
    """Get configuration for a specific collection."""
    return COLLECTION_CONFIGS.get(collection_name, {
        "vector_size": 1536,
        "distance": "Cosine",
        "description": "General purpose collection"
    })


def get_all_collection_names() -> List[str]:
    """Get all collection names."""
    return list(COLLECTION_CONFIGS.keys())
