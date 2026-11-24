from pydantic import BaseModel, EmailStr, Field
from app.models import Role
class RegisterIn(BaseModel):
    full_name: str=Field(min_length=2,max_length=160)
    email: EmailStr
    password: str=Field(min_length=10,max_length=128)
class LoginIn(BaseModel):
    email: EmailStr
    password: str
class UserOut(BaseModel):
    id:int; full_name:str; email:EmailStr; role:Role; is_active:bool
    model_config={"from_attributes":True}
class TokenOut(BaseModel):
    access_token:str; token_type:str="bearer"; user:UserOut
class AnalysisIn(BaseModel):
    document_id:int
    analysis_type:str="complete"
