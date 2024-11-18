"""
Router package
"""

from fastapi import APIRouter, status
from fastapi.security import OAuth2PasswordBearer

from . import users, google_auth


# authentication scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


auth_router = APIRouter(
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)


auth_router.include_router(users.router)
auth_router.include_router(google_auth.router)


__all__ = ["auth_router"]
