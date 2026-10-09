from marshmallow import fields

from app.extensions import ma
from app.models.project import Project


class ProjectSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Project
        load_instance = True
        include_fk = True

    owner_username = fields.String(dump_only=True)
    task_count = fields.Integer(dump_only=True)


project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)
