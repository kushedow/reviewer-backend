import markdown2
from pydantic import BaseModel, Field


class WikiArticle(BaseModel):

    slug: str = Field(..., description="A unique identifier for the article")
    skill: str = Field(..., description="Skill associated with the article")
    skill_name: str = Field(..., description="Name of the skill")
    title: str = Field(..., description="Title of the article")
    article: str = Field(..., description="Content of the article")

    @property
    def html(self) -> str:
        return markdown2.markdown(self.article, extras=["code-friendly", "fenced-code-blocks"])
