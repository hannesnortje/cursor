#!/usr/bin/env python3
"""
Session Manager for AI Agent System.
Handles chat session persistence, restoration, and management.
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ChatSessionData:
    """Persistent chat session data."""

    session_id: str
    chat_type: str
    participants: List[str]
    created_at: str
    last_activity: str
    is_active: bool
    message_count: int
    metadata: Optional[Dict[str, Any]] = None


class SessionManager:
    """Manages chat session persistence and restoration."""

    def __init__(self, sessions_dir: str = ".cursor-agents/chat-sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.active_sessions: Dict[str, ChatSessionData] = {}

        # Load existing sessions
        self._load_existing_sessions()

        logger.info(f"Session manager initialized with directory: {sessions_dir}")

    def _load_existing_sessions(self) -> None:
        """Load existing session data from disk."""
        try:
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    with open(session_file, "r") as f:
                        session_data = json.load(f)
                        session = ChatSessionData(**session_data)
                        self.active_sessions[session.session_id] = session
                        logger.debug(f"Loaded session: {session.session_id}")
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Invalid session file {session_file}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Failed to load existing sessions: {e}")

    def create_session(
        self,
        session_id: str,
        chat_type: str,
        participants: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatSessionData:
        """Create a new chat session."""
        session = ChatSessionData(
            session_id=session_id,
            chat_type=chat_type,
            participants=participants,
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            is_active=True,
            message_count=0,
            metadata=metadata or {},
        )

        self.active_sessions[session_id] = session
        self._save_session(session)

        logger.info(f"Created session: {session_id} ({chat_type})")
        return session

    def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity timestamp."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.last_activity = datetime.now().isoformat()
            self._save_session(session)
            return True
        return False

    def increment_message_count(self, session_id: str) -> bool:
        """Increment message count for a session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.message_count += 1
            self._save_session(session)
            return True
        return False

    def close_session(self, session_id: str) -> bool:
        """Close a chat session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.is_active = False
            session.last_activity = datetime.now().isoformat()
            self._save_session(session)

            logger.info(f"Closed session: {session_id}")
            return True
        return False

    def get_session(self, session_id: str) -> Optional[ChatSessionData]:
        """Get session data by ID."""
        return self.active_sessions.get(session_id)

    def get_active_sessions(self) -> List[ChatSessionData]:
        """Get all active sessions."""
        return [s for s in self.active_sessions.values() if s.is_active]

    def get_sessions_by_type(self, chat_type: str) -> List[ChatSessionData]:
        """Get sessions by chat type."""
        return [s for s in self.active_sessions.values() if s.chat_type == chat_type]

    def get_user_sessions(self, user_id: str) -> List[ChatSessionData]:
        """Get sessions where user is a participant."""
        return [
            s
            for s in self.active_sessions.values()
            if user_id in s.participants and s.is_active
        ]

    def _save_session(self, session: ChatSessionData) -> None:
        """Save session data to disk."""
        try:
            session_file = self.sessions_dir / f"{session.session_id}.json"
            with open(session_file, "w") as f:
                json.dump(session.to_dict(), f, indent=2)

            logger.debug(f"Saved session: {session.session_id}")
        except Exception as e:
            logger.error(f"Failed to save session {session.session_id}: {e}")

    def _delete_session_file(self, session_id: str) -> None:
        """Delete session file from disk."""
        try:
            session_file = self.sessions_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
                logger.debug(f"Deleted session file: {session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session file {session_id}: {e}")

    def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up old inactive sessions."""
        try:
            current_time = datetime.now()
            max_age = current_time.timestamp() - (max_age_hours * 3600)
            cleaned_count = 0

            sessions_to_remove = []

            for session_id, session in self.active_sessions.items():
                if not session.is_active:
                    # Check if session is old enough to clean up
                    last_activity = datetime.fromisoformat(session.last_activity)
                    if last_activity.timestamp() < max_age:
                        sessions_to_remove.append(session_id)

            for session_id in sessions_to_remove:
                del self.active_sessions[session_id]
                self._delete_session_file(session_id)
                cleaned_count += 1

            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} inactive sessions")

            return cleaned_count

        except Exception as e:
            logger.error(f"Failed to cleanup inactive sessions: {e}")
            return 0

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics."""
        total_sessions = len(self.active_sessions)
        active_sessions = len([s for s in self.active_sessions.values() if s.is_active])
        total_messages = sum(s.message_count for s in self.active_sessions.values())

        # Count by type
        type_counts = {}
        for session in self.active_sessions.values():
            chat_type = session.chat_type
            type_counts[chat_type] = type_counts.get(chat_type, 0) + 1

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "inactive_sessions": total_sessions - active_sessions,
            "total_messages": total_messages,
            "sessions_by_type": type_counts,
            "timestamp": datetime.now().isoformat(),
        }

    def export_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session data for backup or analysis."""
        session = self.get_session(session_id)
        if not session:
            return None

        try:
            # Get session file path
            session_file = self.sessions_dir / f"{session_id}.json"

            if session_file.exists():
                with open(session_file, "r") as f:
                    session_data = json.load(f)

                # Add export metadata
                export_data = {
                    "export_info": {
                        "exported_at": datetime.now().isoformat(),
                        "export_version": "1.0",
                    },
                    "session_data": session_data,
                }

                return export_data
            else:
                logger.warning(f"Session file not found: {session_id}")
                return None

        except Exception as e:
            logger.error(f"Failed to export session {session_id}: {e}")
            return None

    def import_session_data(self, session_data: Dict[str, Any]) -> bool:
        """Import session data from backup."""
        try:
            if "session_data" not in session_data:
                logger.error("Invalid session data format")
                return False

            session_info = session_data["session_data"]
            session = ChatSessionData(**session_info)

            # Check if session already exists
            if session.session_id in self.active_sessions:
                logger.warning(
                    f"Session {session.session_id} already exists, skipping import"
                )
                return False

            # Import the session
            self.active_sessions[session.session_id] = session
            self._save_session(session)

            logger.info(f"Imported session: {session.session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to import session data: {e}")
            return False
