from typing import List, TypedDict, Annotated, Sequence, Optional
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
import operator

class EntityNode(BaseModel):
    id: str
    labels: List[str]
    name: str
    description: str
    type: Optional[str] = None

class DocumentNode(BaseModel):
    country: str
    geo_precision: int
    disorder_type: str
    latitude: float
    admin: str
    title: str
    civilian_targeting: bool = False
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

class ChartSpec(BaseModel):
    chart_type: str
    data_fields: List[str]
    title: str
    description: str

class LangGraphInput(BaseModel):
    entity: EntityNode
    documents: List[DocumentNode]
    chart_spec: Optional[ChartSpec] = None

class GraphState(TypedDict):
    input: LangGraphInput
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str

class NodeRequest(BaseModel):
    node_name: str