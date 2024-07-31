from datetime import datetime
from pydantic import BaseModel

class Usuario(BaseModel):
    username: str
    password: str
    role: str
    fecha_creacion: datetime = datetime.now()
    parent_user: str = "TODO"