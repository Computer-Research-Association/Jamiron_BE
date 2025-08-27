from sqlalchemy.orm import sessionmaker

class User(BaseModel):
    username: str
    password: SecretStr