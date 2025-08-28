from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from pydantic import SecretStr



class User(BaseModel):
    username: str
    password: SecretStr