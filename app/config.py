from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    posthog_api_key: str = ""
    posthog_host: str = "https://us.i.posthog.com"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    bigquery_project: str = ""
    bigquery_dataset: str = "reflection"
    bigquery_key_path: str = ""
    bigquery_key_json: str = ""
    anthropic_api_key: str = ""
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    dbt_cron_hour_utc: int = 6

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
