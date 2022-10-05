from sqlalchemy import create_engine
from dressup.config import Config
from dressup.models import Base


def main():
  engine = create_engine(Config.DATABASE_URL)
  Base.metadata.create_all(engine)


if __name__ == "__main__":
  main()
