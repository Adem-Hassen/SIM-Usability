from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    
    # API Configuration
    openai_api_key: str = Field(..., description="OpenAI API key (required)")
    openai_model: str = Field(default="gpt-4o-mini", description="LLM model to use")
    
    # Agent Settings
    max_agent_iterations: int = Field(default=15, description="Max steps per agent")
    max_swarm_rounds: int = Field(default=5, description="Max swarm iterations")
    
    # Paths
    output_dir: Path = Field(default=Path("outputs"), description="Output directory")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Allow OPENAI_API_KEY or openai_api_key
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "screenshots").mkdir(exist_ok=True)
        (self.output_dir / "traces").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)


# Global settings instance
settings = Settings()
