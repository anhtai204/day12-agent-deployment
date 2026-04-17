from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    # App config
    app_name: str = "Production Agent"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    environment: str = "production"
    use_mock_llm: bool = True 

    # Security
    agent_api_key: str = "22042004"
    allowed_origins: List[str] = ["*"]

    # AI Model
    llm_model: str = "gemini-1.5-flash"
    gemini_api_key: str = ""
    openai_api_key: str = ""

    # Infrastructure
    # TẤT CẢ các biến dưới đây sẽ được nạp tự động từ .env hoặc Railway Dashboard
    REDIS_URL: Optional[str] = None
    REDIS_PUBLIC_URL: Optional[str] = None
    REDISHOST: str = "localhost"
    REDISPORT: int = 6379
    REDISUSER: str = "default"
    REDISPASSWORD: str = ""

    def get_redis_url(self) -> str:
        """
        Logic kết nối Redis:
        1. Ưu tiên REDIS_URL (thường là Internal trên Cloud).
        2. Nếu ở Local, dùng REDIS_PUBLIC_URL (Proxy).
        3. Cuối cùng ghép từ Host/Port.
        """
        if self.REDIS_URL:
            return self.REDIS_URL
        
        if self.environment != "production" and self.REDIS_PUBLIC_URL:
            return self.REDIS_PUBLIC_URL
            
        auth = ""
        if self.REDISPASSWORD:
            auth = f"{self.REDISUSER}:{self.REDISPASSWORD}@"
        
        return f"redis://{auth}{self.REDISHOST}:{self.REDISPORT}/0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
