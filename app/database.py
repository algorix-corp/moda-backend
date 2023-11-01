from os import getenv

from dotenv import load_dotenv
from redis import Redis
from sqlmodel import Session, create_engine

load_dotenv()

database_url = (f"postgresql://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}"
                f"@{getenv('POSTGRES_HOST')}:{getenv('POSTGRES_PORT')}/{getenv('POSTGRES_DB')}")

redis = Redis(
    host=getenv("REDIS_HOST"),
    port=getenv("REDIS_PORT"),
    password=getenv("REDIS_PASSWORD"),
    decode_responses=True
)

engine = create_engine(
    database_url,
    echo=False
)

if __name__ == "__main__":
    print(f"REDIS | {redis.info()['redis_version']}")
    with Session(engine) as session:
        print(f"POSTGRES | {session.execute('SELECT version()').first()[0]}")
