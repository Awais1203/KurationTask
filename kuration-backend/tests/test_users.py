"""User endpoint tests for Users API."""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User, AuthRole
from .auth_test import AuthTest


BASE_ENDPOINT = "/users"

# pylint: disable = unused-argument
class TestUsers(AuthTest):
    """
    Unit tests for users APIs
    """

    # LIST USERS
    @pytest.mark.asyncio
    async def test_list_users(
        self, client: AsyncClient, session: AsyncSession
    ):
        """
        Test list users API
        """
        # arrange
        await self.add_role_to_user(session, AuthRole.ADMIN)

        # act
        response = await client.get(
            url=BASE_ENDPOINT,
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            },
        )
        # assert
        assert response.status_code == status.HTTP_200_OK, response.text
        j_resp = response.json()

        # Check if 'items' key exists in the response
        assert "items" in j_resp

        assert "end" in j_resp
        assert "total" in j_resp

        # Check if 'id' key exists in the first item of 'items'
        assert "id" in j_resp["items"][0] and j_resp["items"][0]["id"] == 1

        # Check if 'password' key does not exist in the first item of 'items'
        assert "password" not in j_resp["items"][0]

        # Check if 'groups' key exists in the first item of 'items'
        assert "groups" in j_resp["items"][0]

    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient, session: AsyncSession):
        """
        Test create user API
        """
        # act
        # add admin permission to user
        await self.add_admin_permissions_to_user(session)
        response = await client.post(
            url=f"{BASE_ENDPOINT}/register",
            json={
                "name": "test_user_public",
                "first_name": "Anonymous",
                "last_name": "User",
                "email": "testuser@public.com",
                "password": "T3stpassw0rd",
            },
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            },
        )
        # assert
        assert response.status_code == status.HTTP_200_OK, response.text
        j_resp = response.json()
        assert j_resp["id"] == 2
        db_user = await session.scalar(select(User).where(User.id == j_resp["id"]))
        assert db_user

    @pytest.mark.asyncio
    async def test_get_current_user(
        self, client: AsyncClient, session: AsyncSession
    ):
        """
        Test get user API
        """
        # arrange
        new_user_token = await self.create_more_users(
            client=client,
            session=session,
            user_name="test2",
            user_pass="test2pass",
        )
        await self.add_role_to_user(session, AuthRole.ADMIN, "test2")

        # act
        response = await client.get(
            url=f"{BASE_ENDPOINT}/current_user",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {new_user_token}",
            },
        )
        # assert
        assert response.status_code == status.HTTP_200_OK, response.text
        j_resp = response.json()
        assert "id" in j_resp and j_resp["id"] == 2
        assert "name" in j_resp and j_resp["name"] == "test2"
        assert "password" not in j_resp
        assert "groups" in j_resp

    # GET USER 
    @pytest.mark.asyncio
    async def test_get_user(self, client: AsyncClient, session: AsyncSession):
        """
        Test get user API
        """
        # arrange
        await self.add_role_to_user(session, AuthRole.ADMIN)

        # act
        response = await client.get(
            url=f"{BASE_ENDPOINT}/1",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            },
        )
        # assert
        assert response.status_code == status.HTTP_200_OK, response.text
        j_resp = response.json()
        assert "id" in j_resp and j_resp["id"] == 1
        assert "name" in j_resp and j_resp["name"] == "testuser"
        assert "password" not in j_resp
        assert "groups" in j_resp

    @pytest.mark.asyncio
    async def test_delete_user(
        self, client: AsyncClient, session: AsyncSession
    ):
        # act
        await self.add_admin_permissions_to_user(session)
        response = await client.delete(
            url=f"{BASE_ENDPOINT}/1",
            headers={
                "accept": "application/json",
                "authorization": f"Bearer {self.access_token}",
            },
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        j_resp = response.json()
        assert j_resp["id"] == 1
        assert j_resp["deleted"]

    
    # UPDATE USER
    @pytest.mark.asyncio
    async def test_update_user_base(
        self, client: AsyncClient, session: AsyncSession
    ):
        """
        Test update user API
        """
        # add admin permission to user
        await self.add_admin_permissions_to_user(session)

        # act
        response = await client.patch(
            url=f"{BASE_ENDPOINT}/1",
            json={
                "name": "newname"
            },
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            },
        )
        # assert
        assert response.status_code == status.HTTP_200_OK, response.text
        j_resp = response.json()
        assert "id" in j_resp and j_resp["id"] == 1
        # here we check successful update of record
        assert j_resp["name"] == "newname"
        assert j_resp["token"] == self.access_token
        assert j_resp["refresh_token"] is None