from fastapi import FastAPI, Depends, HTTPException
from fastapi import Form
from api.face_api.auth import authenticate_user, create_access_token
from api.face_api.v1.routes import router as v1_router
from api.face_api.v2.routes import router as v2_router

app = FastAPI(title="FaceCensor API", version="2.0")

@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

# Montar routers versionados
app.include_router(v1_router, prefix="/v1", tags=["v1"])
app.include_router(v2_router, prefix="/v2", tags=["v2"])
