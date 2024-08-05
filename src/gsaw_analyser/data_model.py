from datetime import datetime

from pydantic import BaseModel


class GroundStation(BaseModel):
    id: str
    lat: float
    lon: float
    alt: float


class CommLink(BaseModel):
    id: str


class LinkBudgetAnalysis(BaseModel):
    comm_link_id: str
    ground_station_id: str
    min_elevation_angle: float


class SpacecraftModel(BaseModel):
    id: str
    comm_links: list[CommLink]
    link_budget_analyses: dict[str, LinkBudgetAnalysis]
    tle: list[str]


class GsawDataModel(BaseModel):
    analysis_start_time: datetime
    analysis_end_time: datetime
    ground_stations: list[GroundStation]
    spacecraft: list[SpacecraftModel]
