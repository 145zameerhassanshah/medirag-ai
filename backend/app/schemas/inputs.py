"""HTTP request validation schemas."""
from pydantic import BaseModel, Field, field_validator

class Register(BaseModel):
    name:str=Field(min_length=2,max_length=120)
    email:str=Field(min_length=5,max_length=255)
    password:str=Field(min_length=10,max_length=128)
class Login(BaseModel):
    email:str
    password:str
class UserProfileIn(BaseModel):
    name:str=Field(min_length=2,max_length=120)
class CompanyIn(BaseModel):
    name:str=Field(min_length=2,max_length=180)
    industry:str='Other'
    description:str=''
    website:str=''
    phone:str=''
    address:str=''
    hours:str=''
    policies:str=''
class KBIn(BaseModel):
    name:str=Field(min_length=2,max_length=180)
    description:str=''
class BotIn(BaseModel):
    name:str=Field(min_length=2,max_length=120)
    kb_id:str
    tone:str='Professional'
    greeting:str='How can I help?'
class ProductIn(BaseModel):
    kb_id:str
    name:str=Field(min_length=2,max_length=180)
    sku:str=''
    category:str=''
    description:str=''
    price:str=''
    currency:str='USD'
    availability:str='Unknown'
class ConversationUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator('title')
    @classmethod
    def valid_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('Conversation title cannot be empty')
        return value

class ChatIn(BaseModel):
    company_id:str
    bot_id:str
    knowledgebase_id:str
    conversation_id:str|None=None
    question:str=Field(min_length=1,max_length=2000)
    top_k:int=Field(default=5,ge=1,le=12)
    web_search:bool=False
    threshold:float|None=Field(default=None,ge=-1,le=1)
    @field_validator('question')
    @classmethod
    def valid(cls,value):
        if not value.strip(): raise ValueError('Empty question')
        return value.strip()
