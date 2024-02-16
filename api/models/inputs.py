from pydantic import BaseModel


class WatchlistInput(BaseModel):
    symbol: str


class SignupInput(BaseModel):
    username: str
    first_name: str
    last_name: str
    password: str
    email: str


class SignInInput(BaseModel):
    username: str
    password: str


class User(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
