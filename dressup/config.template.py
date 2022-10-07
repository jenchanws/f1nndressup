class Config:
  SECRET_KEY = None

  BASE_URL = None
  DATABASE_URL = None
  REDIS_URL = None

  TWITCH_CLIENT_ID = None
  TWITCH_CLIENT_SECRET = None

  STREAMER_ID = None  # numeric ID

  TWITCH_AUTH_SCOPES = []

  MODERATOR_ALLOWLIST = {}  # username (all lowercase) -> numeric ID

  DURATIONS = {}  # display text -> number of seconds
