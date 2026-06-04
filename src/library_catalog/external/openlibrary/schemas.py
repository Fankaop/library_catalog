from pydantic import BaseModel, ConfigDict

class OpenLibrarySearchDoc(BaseModel):
    """Документ из поиска Open Library."""
    
    title: str
    author_name: list[str] | None = None
    cover_i: int | None = None
    subject: list[str] | None = None
    publisher: list[str] | None = None
    language: list[str] | None = None
    ratings_average: float | None = None
    
    model_config = ConfigDict(populate_by_name = True)


class OpenLibrarySearchResponse(BaseModel):
    """Ответ от /search.json"""
    
    numFound: int
    docs: list[OpenLibrarySearchDoc]
