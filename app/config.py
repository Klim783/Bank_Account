from pydantic import BaseSettings

class Settings(BaseSettings):
	database_url:str ="postgresql+psycopg2://bank_user:bank_pass@localhost:5490/bank_account"

	class Config:
		env_file = '.env'

settings = Settings()