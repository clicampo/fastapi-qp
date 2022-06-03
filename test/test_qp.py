from typing import Optional

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from fastapi_qp import QueryParam
from pydantic import Field
from pydantic.main import BaseModel


class Sample(BaseModel, QueryParam):
    since: Optional[str] = Field(None, description="A date in the format YYYY-MM-DD")
    until: Optional[str] = Field(None, description="A date in the format YYYY-MM-DD")

app = FastAPI()

@app.get("/")
async def read(
    qp: Sample = Depends(Sample.params())
):
    return qp.dict()

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.json()['since'] == None

    response = client.get("/?since=1")
    assert response.json()['since'] == '1'

    assert Sample(since=1).since == '1'
    assert Sample().to_url() == None
    assert Sample(since=1).to_url() == '?since=1'
    assert Sample(since=1, until=1).to_url() == '?since=1&until=1'
