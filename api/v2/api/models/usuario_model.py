from datetime import datetime
from werkzeug.security import generate_password_hash

class Usuario:
    def __init__(self, username, password, role, parent_user):
        self.username = username
        self.password = password
        self.role = role
        self.fecha_creacion = datetime.now()
        self.parent_user = parent_user

    def save_to_db(self):
        password_hash = generate_password_hash(self.password)
        usuarios_collection.insert_one({
            'username': self.username,
            'password': password_hash,
            'role': self.role,
            'fecha_creacion': self.fecha_creacion,
            'parent_user': self.parent_user
        })
