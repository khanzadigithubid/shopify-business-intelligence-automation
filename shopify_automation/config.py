"""Environment configuration with explicit live-mode validation."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    store_domain: str | None
    access_token: str | None
    api_version: str
    ai_api_key: str | None
    ai_base_url: str
    ai_model: str
    timezone: str
    low_stock_threshold: int
    request_timeout_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            store_domain=os.getenv("SHOPIFY_STORE_DOMAIN"),
            access_token=os.getenv("SHOPIFY_ACCESS_TOKEN"),
            api_version=os.getenv("SHOPIFY_API_VERSION", "2025-10"),
            ai_api_key=os.getenv("AI_API_KEY"),
            ai_base_url=os.getenv("AI_BASE_URL", "https://openrouter.ai/api/v1"),
            ai_model=os.getenv("AI_MODEL", "openai/gpt-4o-mini"),
            timezone=os.getenv("REPORT_TIMEZONE", "Asia/Karachi"),
            low_stock_threshold=int(os.getenv("LOW_STOCK_THRESHOLD", "10")),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
        )

    def require_shopify(self) -> None:
        missing = []
        if not self.store_domain:
            missing.append("SHOPIFY_STORE_DOMAIN")
        if not self.access_token:
            missing.append("SHOPIFY_ACCESS_TOKEN")
        if missing:
            raise RuntimeError(
                "Missing Shopify configuration: " + ", ".join(missing) +
                ". Use --demo only for local development."
            )

