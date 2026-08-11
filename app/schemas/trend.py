from sqlmodel import SQLModel


class TrendItemResponse(SQLModel):
    keyword: str
    trend_score: float | None
    mention_count: int | None
    outlet_diversity: int | None