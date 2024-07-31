from pydantic import BaseModel
from datetime import datetime

class Proveedor(BaseModel):
    _id: str
    nombre: str
    razon_social: str
    nombre_contacto: str
    email: str
    direccion_fiscal: str
    tipo_servicio: str
    criticidad: str
    bloqueo: bool = False
    fecha_creacion: datetime = datetime.now()
