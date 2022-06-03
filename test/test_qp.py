from typing import Optional

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from fastapi_qp import QueryParam
from pydantic import Field, ValidationError
from pydantic.error_wrappers import ValidationError
from pydantic.main import BaseModel


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

app = FastAPI()

@app.get("/")
async def read(params: CommonParams = Depends(CommonParams.params())):
    return params.dict()

client = TestClient(app)

def test_no_params():
    response = client.get("/")
    assert response.json()['since'] == None

def test_single_param():
    response = client.get("/" + CommonParams(since='2020-01-01').to_url())
    assert response.json()['since'] == '2020-01-01'

def test_multiple_params():
    response = client.get("/" + CommonParams(since='2020-01-01', limit=50).to_url())
    assert response.json()['since'] == '2020-01-01'
    assert response.json()['limit'] == 50

def test_invalid_param():
    with pytest.raises(ValidationError):
        client.get("/" + CommonParams(limit=1001).to_url())

def test_no_param_url():
    assert CommonParams().to_url() == None
