from fastapi import FastAPI
from app.routes import file_routes
from app.routes import structure_routes
from app.routes import nlp_routes
from app.services.visualization import hierarchy_to_mermaid
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Document Handling API", version="1.0")
# CORS for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for stricter
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(file_routes.router)
app.include_router(structure_routes.router)
app.include_router(nlp_routes.router)

@app.get("/")
def root():
    return {"message": "Document Handling API Ready"}


@app.post("/visualization/mermaid")
async def get_mermaid_chart(hierarchy: dict):
    mermaid_code = hierarchy_to_mermaid(hierarchy)
    return {"mermaid": mermaid_code}