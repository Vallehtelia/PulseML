"""Model registry API routes."""

from dataclasses import asdict
from typing import List

from fastapi import APIRouter

from . import schemas
from .registry import get_templates

router = APIRouter()


@router.get("/templates", response_model=List[schemas.ModelTemplateSchema])
async def list_model_templates() -> List[schemas.ModelTemplateSchema]:
    """Return registered model templates."""

    templates = []
    for template_def in get_templates():
        templates.append(
            schemas.ModelTemplateSchema(
                id=template_def.id,
                name=template_def.name,
                task_type=template_def.task_type,
                default_hparams=template_def.default_hparams,
                hyperparam_schema=[
                    schemas.HyperParamField(**asdict(field))
                    for field in template_def.hyperparam_schema
                ],
            )
        )
    return templates

