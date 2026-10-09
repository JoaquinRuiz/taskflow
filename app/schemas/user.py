from app.extensions import ma
from app.models.user import User


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True


user_schema = UserSchema()
users_schema = UserSchema(many=True)
