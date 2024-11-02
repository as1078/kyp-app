from typing import List
from pydantic import BaseModel
class EntityNode(BaseModel):
    labels: List[str]
    name: str
    description: str
    type: str

class DocumentNode(BaseModel):
    country: str
    geo_precision: int
    disorder_type: str
    latitude: float
    admin: str
    title: str
    civilian_targeting: str
    sub_event_type: str
    actor2: str
    actor1: str
    event_type: str
    fatalities: int
    interaction: int
    time_precision: int
    location: str
    id: str
    region: str
    timestamp: str
    longitude: float

class LangGraphInput(BaseModel):
    entities: List[EntityNode]
    documents: List[DocumentNode]

class GraphState(BaseModel):
    input: LangGraphInput
    output: str = ""
    current_step: str = ""