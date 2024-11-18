"""CLI commands for database management"""

import asyncio

import typer
from alembic import config
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload
from typing_extensions import Annotated

from app import settings
from app.db import models
from app.db.database import DBManager
from app.db.models import AuthRole, Group, User
from app.routers.utils import get_engine_from_session
from app.utils import encrypt_password
from cli.manage_forms import async_create

# create CLI app
app = typer.Typer()


async def async_create_groups_and_vault() -> None:
    """
    Asynchronous create_groups_and_vault.
    """

    db_manager = DBManager()
    async with db_manager.get_session() as session:
        # create default roles
        groups = [
            Group(name=AuthRole.ADMIN, description="Administrators"),
            Group(name=AuthRole.DATA_EXPLORER, description="Data explorers"),
        ]
        session.add_all(groups)

        await session.commit()


async def async_create_all() -> None:
    """
    Asynchronous create_all.
    """
    db_manager = DBManager()
    async with db_manager.get_session() as session:
        engine = get_engine_from_session(session)
        async with engine.begin() as conn:
            # create database tables
            await conn.run_sync(models.Base.metadata.create_all)

    await async_create_groups_and_vault()
    await async_create_user(
        name="testadmin", password="testpass", superuser="true", role=" --superuser"
    )


async def async_create_role(name: str, description: str = "") -> None:
    """
    Asynchronous create_role.
    """

    db_manager = DBManager()
    async with db_manager.get_session() as session:
        # check if group exists
        group = await session.scalar(select(Group).filter_by(name=name))
        if not group:
            # create group
            group = Group(name=name, description=description)
            session.add(group)
            await session.commit()


async def async_delete_role(name: str) -> None:
    """
    Asynchronous delete_role.
    """

    db_manager = DBManager()
    async with db_manager.get_session() as session:
        # load group
        group = await session.scalar(select(Group).filter_by(name=name))
        if group:
            # delete group
            await session.delete(group)
            await session.commit()


async def async_delete_user(name: str) -> None:
    """
    Asynchronous delete_user.
    """

    db_manager = DBManager()
    async with db_manager.get_session() as session:
        # load user
        user = await session.scalar(select(User).filter_by(name=name))
        if user:
            # delete user
            await session.delete(user)
            await session.commit()


async def async_create_user(
    name: str, password: str, superuser: bool, role: AuthRole | None = None
) -> None:
    """
    Asynchronous create_user.
    """

    # create database session
    db_manager = DBManager()
    async with db_manager.get_session() as session:
        # check if user exists
        user = await session.scalar(
            select(User).filter_by(name=name).options(selectinload(User.groups))
        )
        if not user:
            # encrypt password
            encrypted_pwd = encrypt_password(password)
            # create user
            user = User(name=name, password=encrypted_pwd, external_user_id=None)
            session.add(user)
            await session.flush()
            # reload user with groups
            user = await session.scalar(
                select(User).filter_by(name=name).options(selectinload(User.groups))
            )
            assert user

            # check if role specified for user
            group: Group | None = None
            if superuser:
                role = AuthRole.ADMIN
            if role:
                # load role
                group = await session.scalar(select(Group).filter_by(name=role))

            if group:
                # assign role to user
                user.groups.append(group)

            # commit the transaction
            await session.commit()
        else:
            raise ValueError("User already exists.")


async def async_drop_all() -> None:
    """
    Asynchronous drop_all.
    """

    table_names: list[str] = []

    # need to create a new session otherwise drop_all hangs if
    # called on the same session instance of select(TableDef)
    db_manager = DBManager()
    async with db_manager.get_session() as session:
        engine = get_engine_from_session(session)
        async with engine.begin() as conn:
            if table_names:
                # drop submission tables
                drop_sql = f"drop table if exists {','.join(table_names)};"
                await conn.execute(text(drop_sql))
                # await conn.commit()

            # drop other tables in model
            await conn.run_sync(models.Base.metadata.drop_all)


@app.command()
def create_all() -> None:
    """
    Create database tables
    """

    asyncio.run(async_create_all())


# pylint: disable = invalid-name
@app.command()
def drop_all(y: Annotated[bool, typer.Option("-y")] = False) -> None:
    """
    Delete all tables from database
    """

    if not y:
        confirm = input("Confirm dropping all tables from database? (y/N) ")
        if confirm:
            y = confirm.upper() == "Y"

    if y:
        asyncio.run(async_drop_all())


@app.command()
def create_user(
    name: str,
    password: str,
    superuser: bool = False,
    role: AuthRole = typer.Argument(None),
) -> None:
    """
    Create a new user
    """

    asyncio.run(
        async_create_user(name=name, password=password, superuser=superuser, role=role)
    )


@app.command()
def delete_user(name: str) -> None:
    """
    Delete a user
    """

    confirm = input(f"Confirm deleting user '{name}'? (y/N) ")
    if confirm and confirm.upper() == "Y":
        asyncio.run(async_delete_user(name=name))


if __name__ == "__main__":
    # start CLI App
    app()
