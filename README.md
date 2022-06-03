<div align="center">

### FastAPI Query Parameters

Empower your query parameters setup on FastAPI through Pydantic

</div>

#### Installation
```bash
poetry add fastapi-qp
```

#### Usage
You can just define a Pydantic schema describing your query parameters, and extends the class with `QueryParam`, which you'll import from the package

```python
# schemas/params/common.py
from fastapi_qp import QueryParam

class CommonParams(BaseModel, QueryParam):
    since: Optional[str] = Field(None, description="A date in the format YYYY-MM-DD")
    until: Optional[str] = Field(None, description="A date in the format YYYY-MM-DD")
    limit: int = Field(100, description="How many entries will be returned")
    offset: int = Field(0, description="Entries ignored from the start of result list") 
```

And then, you can use the `.params()` method to return a dependency to your route

```python
# app/main.py

@app.get("/items/")
def read_items(params: CommonParams = Depends(CommonParams.params())):
    return get_items(offset=params.offset, limit=params.limit)
```

##### Testing

In testing, you can use the `.to_url()` method to get a URL component with the params encoded

```python
def _get_items(params: CommonParams):
    client = TestClient(app)
    
    query = params.to_url()
    return client.get("/items/" + query)

def test_items():
    response = _get_items(CommonParams(limit=10))
    assert len(response.json()) <= 10
```

#### Composing parameters
You can combine different parameters together through inheritance

```python
# schemas/params/common.py

class DateParams(BaseModel, QueryParam):
    since: Optional[str] = Field(
        None, 
        description="A date in the format YYYY-MM-DD",
        min_length=10,
        max_length=10,
        regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
    )
    until: Optional[str] = Field(
        None, 
        description="A date in the format YYYY-MM-DD",
        min_length=10,
        max_length=10,
        regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    )

class PaginationParams(BaseModel, QueryParam):
    offset: int = Field(
        0, 
        description="Items ignored from the beginning of the list",
        gte=0,
    )
    limit: int = Field(
        100, 
        description="Number of items per result",
        ge=0,
        le=1000
    )

class CommonParams(PaginationParams, DateParams):
    pass
``` 

### Acknowledgments
This implementation is greatly inspired by @markus1978, on [this](https://github.com/tiangolo/fastapi/issues/318#issuecomment-691121286) issue.