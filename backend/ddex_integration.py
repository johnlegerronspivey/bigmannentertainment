# Integration file to add DDEX router to main server
from .server import app
from .ddex_endpoints import ddex_router

# Include DDEX router in main application
app.include_router(ddex_router)