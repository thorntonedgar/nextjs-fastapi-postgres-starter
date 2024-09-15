from sqlalchemy import select
from sqlalchemy.orm import Session
from db_engine import sync_engine
from models import User, Thread


def seed_user_if_needed():
    with Session(sync_engine) as session:
        with session.begin():
            if session.execute(select(User)).scalar_one_or_none() is not None:
                print("User already exists, skipping seeding")
            else: 
                print("Seeding user")
                session.add(User(name="Alice"))
                session.commit()



            # Check if the thread exists
            if session.execute(select(Thread)).scalar_one_or_none() is not None:
                print("Thread already exists, skipping thread seeding")
            else:
                print("Seeding thread")
                session.add(Thread(name="General Chat"))
                session.commit()
            return True