from pydantic import BaseModel, EmailStr, Field, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)

    @field_validator("email")
    @classmethod
    def force_lowercase(cls, value: str | None) -> str | None:
        if value is not None:
            return value.lower()
        return value


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
