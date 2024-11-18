# app/auth/google_auth.py

import os
from fastapi import APIRouter
from fastapi.security import OAuth2AuthorizationCodeBearer
from httpx import AsyncClient
from app.db.models import User, AuthMode
from app.dependencies import dbManager
from sqlalchemy import select


router = APIRouter(
    tags=["users"],
    responses={404: {"description": "Not found."}},
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token",
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


@router.get("/auth/google")
async def google_auth():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&response_type=code&scope=email profile"
    }


@router.get("/auth/google/callback")
async def google_callback(code: str, db_manager: dbManager):
    async with AsyncClient() as client:
        # Exchange code for token

        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        # Get user info
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info = user_info_response.json()

        # Check if user exists in your database
        async with db_manager.get_session() as session:
            stmt = select(User).where(User.email == user_info["email"])
            result = await session.execute(stmt)
            user = result.scalars().first()

            if not user:
                # Create a new user if not exists
                user = User(
                    name=user_info["name"],
                    email=user_info["email"],
                    auth_mode=AuthMode.GOOGLE,
                    email_verified=True,
                    external_user_id=user_info["id"],
                    # Add other fields as necessary
                )
                session.add(user)
                await session.commit()

        # Return the access token instead of generating a JWT
        return {"access_token": access_token}
