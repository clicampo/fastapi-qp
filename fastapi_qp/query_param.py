import inspect
from types import FunctionType
from typing import Dict

from fastapi import HTTPException, Query
from pydantic import BaseModel, ValidationError


class QueryParam():
    @classmethod
    def params(_class: BaseModel):
        """
        Turns this schema into a parseable dependency for FastAPI.

        Example:
            >>> class MyQueryParams(BaseModel, QueryParam):
            >>>     foo: str = Field(..., description="Foo", ...)
            >>>     bar: str = Field(..., description="Bar", ...)
            >>>
            >>> @app.get("/")
            >>> async def read(params: MyQueryParams = Depends(MyQueryParams.params())):
            >>>     return params.dict()
        """
        name = f"{_class.__name__}QP"
        names = []
        annotations: Dict[str, type] = {}
        defaults = []
        for field_model in _class.__fields__.values():
            field_info = field_model.field_info
            names.append(field_model.name)
            annotations[field_model.name] = field_model.outer_type_
            defaults.append(Query(field_model.default, description=field_info.description))
        code = inspect.cleandoc('''
        def %s(%s):
            try:
                return %s(%s)
            except ValidationError as e:
                errors = e.errors()
                for error in errors:
                    error['loc'] = ['query'] + list(error['loc'])
                raise HTTPException(422, detail=errors)
        ''' % (
            name, ', '.join(names), _class.__name__,
            ', '.join(['%s=%s' % (name, name) for name in names])))

        compiled = compile(code, 'string', 'exec')
        env = {_class.__name__: _class}
        env.update(**globals())
        new_class = FunctionType(compiled.co_consts[0], env, name)
        new_class.__annotations__ = annotations
        new_class.__defaults__ = (*defaults,)
        return new_class

    def to_url(self):
        """
        Transforms the query params into a encoded URL component.
        Returns None if there are no params.

        Example:
            >>> class MyQueryParams(BaseModel, QueryParam):
            >>>     foo: str = Field(..., description="Foo", ...)
            >>>     bar: str = Field(..., description="Bar", ...)
            >>>
            >>> @app.get("/")
            >>> async def read(params: MyQueryParams = Depends(MyQueryParams.params())):
            >>>     return params.dict()
            >>>
            >>> def test_query_params():
            >>>     client = TestClient(app)
            >>>     response = client.get("/" + (params.to_url() or ""))
            >>>     assert response.json()['foo'] == 'bar'

        Returns:
            `None/str`: `None` if there are no params, otherwise a URL encoded string.
        """
        instance: BaseModel = self
        params = [
            f'{name}={value}' for name, value in instance.dict(exclude_unset=True).items()
        ]
        return f"?{'&'.join(params)}" if len(params) > 0 else None
