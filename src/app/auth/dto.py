from pydantic import BaseModel, SecretStr

class LoginIn(BaseModel):
    username: str
    password: SecretStr

class LoginOut(BaseModel):
    session_token: str