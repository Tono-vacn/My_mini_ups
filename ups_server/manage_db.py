from sqlalchemy import create_engine, MetaData, inspect, text, Table, Sequence
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

DATABASE_URI = "postgresql://postgres:abc123@localhost:5432/db"
# DATABASE_URI = 'postgresql://postgres:passw0rd@database:5432/postgres'

engine = create_engine(DATABASE_URI, echo=False)
session_local = sessionmaker(autocommit=False, expire_on_commit=False, bind=engine)

# Reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)

World = Base.classes.myups_world
Account = Base.classes.myups_account_tmp
Truck = Base.classes.myups_truck_set
Package = Base.classes.myups_package_tmp
BaseUser = Base.classes.auth_user

def delete_all():
    meta = MetaData()
    meta.reflect(bind=engine)
    meta.drop_all(bind=engine)
    
    session = session_local()
    inspector = inspect(engine)
    for sequence_name in inspector.get_sequence_names():
        sequence = Sequence(sequence_name)
        session.execute(sequence.drop(bind=engine, checkfirst=True))
        session.execute(sequence.create(bind=engine))
    
def init_db():

    # Create a new session
    session = session_local()

    try:
        meta = MetaData()
        meta.reflect(bind=engine)

        for table in reversed(meta.sorted_tables):
            session.execute(table.delete())

        inspector = inspect(engine)
        for sequence in inspector.get_sequence_names():
            session.execute(text(f"ALTER SEQUENCE {sequence} RESTART WITH 1"))

        session.commit()

        print("Finished delete")

    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()

    finally:
        session.close()
        
def print_table(Table):
    # Create a new session
    session = session_local()

    # Query all rows in the World table
    entries = session.query(Table).all()

    # Print all rows
    for entry in entries:
        print(entry)

    # Close the session
    session.close()

def does_world_exist(world_id):
    session = session_local()
    try:
        world = session.query(World).filter(World.world_id == world_id).first()
        return world is not None
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()
        
if __name__ == "__main__":
    delete_all()