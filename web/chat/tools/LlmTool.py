JSON_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean"}

def _schema(tp) -> dict:
    """Python type -> JSON schema fragment."""
    from typing import get_origin, get_args, Annotated

    description = None
    if get_origin(tp) is Annotated:
        tp, *meta = get_args(tp)
        description = next((m for m in meta if isinstance(m, str)), None)

    if get_origin(tp) is list:
        (item,) = get_args(tp) or (str,)
        out = {"type": "array", "items": _schema(item)}
    elif tp in JSON_TYPES:
        out = {"type": JSON_TYPES[tp]}
    else:
        raise TypeError(f"unsupported parameter type: {tp}")

    if description:
        out["description"] = description
    return out

class LlmTool:
    name: str
    description: str

    def execute(self, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_definition(cls):
        import inspect
        from typing import get_type_hints

        signature = inspect.signature(cls.execute)
        type_hints = get_type_hints(cls.execute, include_extras=True)

        properties = {}
        required = []

        for param_name, param in signature.parameters.items():
            if param_name == "self":
                continue
            if param_name not in type_hints:
                raise TypeError(f"{cls.__name__}.execute: '{param_name}' needs a type annotation")
            properties[param_name] = _schema(type_hints[param_name])
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": cls.name,
                "description": cls.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
