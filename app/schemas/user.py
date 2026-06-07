from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
	email: EmailStr = Field(..., example="johndoe@example.com", max_length=120)
	password: str
	full_name: Optional[str] = None


class UserLogin(BaseModel):
	email: EmailStr
	password: str


class UserOut(BaseModel):
	id: int
	email: EmailStr
	full_name: Optional[str] = None

	model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
	access_token: str
	token_type: str


class AuthResponse(BaseModel):
	"""Login/register response: token plus the authenticated user."""

	access_token: str
	token_type: str = "bearer"
	user: UserOut
