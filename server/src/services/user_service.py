"""User service for profile data and session inspection/revocation."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ForbiddenException, NotFoundException
from src.models.users import User
from src.repositories.token_repo import token_repository
from src.repositories.user_repo import user_repository
from src.schemas.auth import MessageResponse
from src.schemas.user import SessionResponse, UserMeResponse


class UserService:
    """Service handling profile inspection and user session management."""

    async def get_me(self, user: User) -> UserMeResponse:
        """Return profile information for current authenticated user."""
        return UserMeResponse.model_validate(user)

    async def list_active_sessions(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        current_session_id: uuid.UUID | None = None,
    ) -> list[SessionResponse]:
        """List active server-side sessions for authenticated user."""
        sessions = await user_repository.get_user_sessions(db, user_id, only_active=True)
        results: list[SessionResponse] = []
        for s in sessions:
            dto = SessionResponse(
                id=s.id,
                device_info=s.device_info,
                ip_address=s.ip_address,
                client_type=s.client_type,
                is_revoked=s.is_revoked,
                created_at=s.created_at,
                last_used_at=s.last_used_at,
                is_current=(s.id == current_session_id),
            )
            results.append(dto)
        return results

    async def revoke_session_by_id(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> MessageResponse:
        """Revoke a specific session owned by user (BOLA protection)."""
        session = await user_repository.get_session_by_id(db, session_id)
        if not session:
            raise NotFoundException("Session not found.")
        if session.user_id != user_id:
            raise ForbiddenException("Cannot revoke a session belonging to another user.")

        await user_repository.revoke_session(db, session_id)
        await token_repository.create_audit_log(
            db,
            action="SESSION_REVOKED_MANUALLY",
            resource_type="user_session",
            resource_id=str(session_id),
            actor_user_id=user_id,
            ip_address=client_ip,
            user_agent=user_agent,
        )
        return MessageResponse(message="Session revoked successfully.")


user_service = UserService()
