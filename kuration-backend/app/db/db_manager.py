from app.db.database import DBManager, DBHost

# Dependency to get the database session
db_manager = DBManager(DBHost.LEADER)


# Dependency to get the database session
async def get_db():
    async with db_manager.get_session() as db:
        yield db
