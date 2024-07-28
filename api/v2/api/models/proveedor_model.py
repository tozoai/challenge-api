from datetime import datetime

class Proveedor:
    def __init__(self, nombre, razon_social, nombre_contacto, email, direccion_fiscal, tipo_servicio, criticidad, parent_user, bloqueo=False):
        self.nombre = nombre
        self.razon_social = razon_social
        self.nombre_contacto = nombre_contacto
        self.email = email
        self.direccion_fiscal = direccion_fiscal
        self.tipo_servicio = tipo_servicio
        self.criticidad = criticidad
        self.bloqueo = bloqueo
        self.parent_user = parent_user
        self.fecha_creacion = datetime.now()

    def save_to_db(self):
        result = proveedores_collection.insert_one(self.__dict__)
        self._id = result.inserted_id
