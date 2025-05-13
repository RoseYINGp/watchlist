import os
from  dotenv import load_dotenv

detenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(detenv_path):
    load_dotenv(detenv_path)

from watchlist import app