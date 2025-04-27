from pydantic_settings import BaseSettings


class Config(BaseSettings):
    SAMBANOVA_API_KEY: str
    SAMBANOVA_BASE_URL: str
    LLM_REASONING: str
    LLM_REGULAR: str
    TAVILY_API_KEY: str

config = Config()