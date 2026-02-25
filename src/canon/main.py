from fastapi import FastAPI

app = FastAPI(
    title="Canon - NizamIQ Prompt Registry",
    description="A centralized, version-controlled registry for all AI agent prompts used in the NizamIQ ecosystem.",
    version="0.1.0",
)

@app.get("/healthz", status_code=200)
async def health_check():
    return {"status": "ok"}
