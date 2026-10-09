from marshmallow import fields

from app.extensions import ma
from app.models.task import Task, Tag


class TagSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tag
        load_instance = True


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True
        include_fk = True

    tags = fields.List(fields.String(), dump_only=True)
    assignee_username = fields.String(dump_only=True)
    project_name = fields.String(dump_only=True)


tag_schema = TagSchema()
tags_schema = TagSchema(many=True)
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
