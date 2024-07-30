from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

def role_required(role):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_role = get_jwt_identity()
            if current_role != role:
                return {"msg": "Access denied: insufficient permissions"}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator