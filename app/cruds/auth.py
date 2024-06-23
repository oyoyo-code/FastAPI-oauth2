from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.engine.cursor import CursorResult
from typing import Union
from pydantic import EmailStr
from logging import getLogger

from app.schemes import user as user_scheme
from app.utils import error

logger = getLogger("uvicorn")

async def create_user(db: AsyncSession, user_create:user_scheme.CreateUser) -> user_scheme.DatabaseUser:
    preparation = text("""
                            SELECT *
                            FROM user
                            WHERE :email in (SELECT DISTINCT email
                                             FROM user)
                                OR :username in (SELECT DISTINCT username
                                                FROM user)
                            LIMIT 1;
                       """)
    
    result:CursorResult = await db.execute(preparation,{"email":user_create.email,"username":user_create.username})

    if result.first() is not None:
        raise error.DuplicateError("The username or email address has been already enrolled.")

    statement = text("""
                        INSERT INTO user (email, password, username)
                        VALUES (:email, :password, :username)
                    """)

    await db.execute(statement,{"email":user_create.email,"password":user_create.password,"username":user_create.username})

    last_user_id:int = (await db.execute(text("SELECT LAST_INSERT_ID() FROM user;"))).scalar()
    result:CursorResult = await db.execute(text("SELECT * FROM user WHERE id = :user_id;"),{"user_id":last_user_id})

    await db.commit()

    return user_scheme.DatabaseUser(**dict(zip(result.keys(),result.one())))


async def get_user(db:AsyncSession,email:EmailStr) -> user_scheme.DatabaseUser:
    statement = text("""
                        SELECT *
                        FROM user
                        WHERE email = :email
                        LIMIT 1;
                    """)

    result:CursorResult = await db.execute(statement,{"email":email})

    user = result.first()

    return False if user is None else user_scheme.DatabaseUser(**dict(zip(result.keys(),user)))  # admit returning None.


async def validate_user(db:AsyncSession,email:EmailStr) -> bool:
    statement = text("""
                        SELECT *
                        FROM user
                        WHERE email = :email;
                    """)

    result:CursorResult = await db.execute(statement,{"email":email})
    
    return False if result.first() is None else True


async def edit_user(db:AsyncSession, edit_user:user_scheme.ModifyUser,user_id:int) -> Union[user_scheme.DatabaseUser,bool]:
    modification_list = [ f"{i} = '{j}'" for i,j in dict(edit_user).items() if j is not None]
    if len(modification_list) == 0:
        return False
    setter_sentence = modification_list[0] if len(modification_list) == 1 else ", ".join(modification_list)
    statement = text(f"""
                        UPDATE user
                        SET {setter_sentence}
                        WHERE id = :id;
                    """)
    await db.execute(statement,{"id":user_id})
    result:CursorResult = await db.execute(text("SELECT * FROM user WHERE id = :id"),{"id":user_id})

    await db.commit()

    return user_scheme.DatabaseUser(**dict(zip(result.keys(),result.one())))


async def reset_pwd_user(db:AsyncSession,user_id:int,hashed_pwd:int) -> user_scheme.DatabaseUser:
    statement = text("""
                        UPDATE user
                        SET password = :password
                        WHERE id = :id;
                    """)
    
    await db.execute(statement,{"password":hashed_pwd,"id":user_id})

    result:CursorResult = await db.execute(text("SELECT * FROM user WHERE id = :id"),{"id":user_id})

    await db.commit()

    return user_scheme.DatabaseUser(**dict(zip(result.keys(),result.one())))


async def delete_user(db:AsyncSession,user_id:int):
    statement = text("""
                        DELETE FROM user
                        WHERE id = :id;
                    """)
    
    await db.execute(statement,{"id":user_id})
    await db.commit()

    return


# logger.info(result.scalar())
# 28
# logger.info(result.one())
# (29, 'aaam@gmail.com', '$2b$12$95gPX4BmTJV4iQyp9ugT6.Jc5feU5k4EZcv4UEMnz14MnkzjWY4KC', 'aaam')
# logger.info(result.first())
# (29, 'aaam@gmail.com', '$2b$12$95gPX4BmTJV4iQyp9ugT6.Jc5feU5k4EZcv4UEMnz14MnkzjWY4KC', 'aaam')
# logger.info(result.all())
# [(30, 'aaan@gmail.com', '$2b$12$4jKUT8dp7oFqszAipSCZQeZbiBTCkfq9gE2BgIduMuf4DPiSsXOBm', 'aaan')]
# allではセッションが閉じない。