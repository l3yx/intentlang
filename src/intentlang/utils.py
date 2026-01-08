from typing import Type, Annotated
from pydantic import create_model, Field, TypeAdapter
from pydantic.json_schema import WithJsonSchema
from .models import IntentIO


def _try_json_schema(x):
    try:
        TypeAdapter(x).json_schema()
        return True
    except Exception:
        return False


def _is_type(obj) -> bool:
    if hasattr(obj, "__origin__"):
        return True
    if isinstance(obj, type):
        return True
    return False


def create_io(**field_definitions) -> Type[IntentIO] | IntentIO:
    fields = {}
    values = {}
    has_values = False

    for field_name, definition in field_definitions.items():
        if len(definition) != 2:
            raise ValueError(
                f"Field '{field_name}' must be a tuple of (value_or_type, description)")

        first, second = definition
        if _is_type(first):
            ok = _try_json_schema(first)
            field_type = first if ok else Annotated[first, WithJsonSchema({})]
            fields[field_name] = (field_type, Field(description=second))
        else:
            ok = _try_json_schema(type(first))
            field_type = type(first) if ok else Annotated[type(
                first), WithJsonSchema({})]
            fields[field_name] = (field_type, Field(description=second))
            values[field_name] = first
            has_values = True

    model_class = create_model("_", __base__=IntentIO, **fields)
    if has_values:
        return model_class(**values)
    else:
        return model_class
