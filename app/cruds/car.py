from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.engine.cursor import CursorResult
from typing import List, Optional
from logging import getLogger

from app.schemes import car as car_scheme
from app.schemes import user as user_scheme
from app.models import car as car_model
from app.utils import error

logger = getLogger("uvicorn")

async def create_active_car(db: AsyncSession, car_create:car_scheme.CreateCar) -> car_scheme.ResponseCar:
    preparation = text("""
                            SELECT *
                            FROM car
                            WHERE :car_name in (SELECT DISTINCT car_name
                                            FROM car
                                            WHERE car.user_id = :user_id)
                            LIMIT 1;
                        """)
    
    result:CursorResult = await db.execute(preparation,{"car_name":car_create.car_name, "user_id":car_create.user_id})

    if result.first() is not None:
        raise error.DuplicateError("The car has been already enrolled.")

    car = car_model.Car(**car_create.dict())
    # sqlalchemyのメソッドを用いて簡潔にデータベースとやり取りをしたいという時、
    # 必ず、どのテーブルと連絡するか明示するために、modelのインスタンス化を通して、データをやり取りしないといけない。

    db.add(car)
    await db.commit()
    await db.refresh(car)

    # addでセッション（python と mysqlとのやり取りの結びつき）にcarインスタンスが登録され、refreshにおいてデータベースでの変更がインスタンスに反映される。
    # もし、セッションを閉じたかったら、expireするだけでいい。

    result:CursorResult = await db.execute(text("SELECT email,username FROM user WHERE id = :id"),{"id":car.user_id})
    user_info = user_scheme.ConcatUserFromCar(**dict(zip(result.keys(),result.one())))

    car_info = dict(car_create)

    car_info.update({"id":car.id, "username":user_info.username,"email":user_info.email})

    return car_scheme.ResponseCar(**car_info)


async def get_active_cars(db:AsyncSession) -> car_scheme.ResponseCar:
    statement = text("""
                        SELECT car.*, user.username, user.email
                        FROM car
                        JOIN user
                        ON car.user_id = user.id
                    """)
    
    result:CursorResult = await db.execute(statement)

    car = result.first()
    if car is None:
        raise error.NoObjectError("There is no car you want.")

    return car_scheme.ResponseCar(**dict(zip(result.keys(),car)))


async def get_active_car(db:AsyncSession, car_id:int) -> car_scheme.ResponseCar:
    statement = text("""
                        SELECT car.*, user.username, user.email
                        FROM car
                        JOIN user
                        ON car.user_id = user.id
                        WHERE car.id = :id;
                    """)
    
    result:CursorResult = await db.execute(statement,{"id":car_id})

    car = result.first()
    if car is None:
        raise error.NoObjectError("There is no car you want.")

    return car_scheme.ResponseCar(**dict(zip(result.keys(),car)))


async def edit_active_car(db:AsyncSession,car_edit:car_scheme.ModifyCar, car_id:int) -> car_scheme.ResponseCar:
    modification_list = [ f"{i} = '{j}'" for i,j in dict(car_edit).items() if j is not None]
    if len(modification_list) == 0:
        return False
    setter_sentence = modification_list[0] if len(modification_list) == 1 else ", ".join(modification_list)

    statement = text(f"""
                        UPDATE car
                        SET {setter_sentence}
                        WHERE id = :id;
                    """)
    
    await db.execute(statement,{"id":car_id})

    selector = text("""
                        SELECT car.*, user.username, user.email
                        FROM car 
                        JOIN user 
                        ON car.user_id = user.id 
                        WHERE car.id = :id
                    """)

    result:CursorResult = await db.execute(selector,{"id":car_id})

    await db.commit()

    return car_scheme.ResponseCar(**dict(zip(result.keys(),result.one())))


async def delete_active_car(db:AsyncSession, car_id:int):
    statement = text("""
                        DELETE FROM car
                        WHERE id = :id;
                    """)
    
    await db.execute(statement,{"id":car_id})
    await db.commit()

    return


