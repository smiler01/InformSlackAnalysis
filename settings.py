# coding: utf-8
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

OAUTH_ACCESS_TOKEN = os.environ.get("OAUTH_ACCESS_TOKEN")
WEB_HOOK_URL = os.environ.get("WEB_HOOK_URL")
