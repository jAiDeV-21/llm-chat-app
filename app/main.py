from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat, conversations

app = FastAPI(title="Chat Application")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(conversations.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}