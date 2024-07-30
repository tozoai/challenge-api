from datetime import datetime
from pydantic import BaseModel, SecretStr

class Usuario(BaseModel):
    username: str
    password: SecretStr
    role: str
    fecha_creacion: datetime = datetime.now()
    parent_user: str