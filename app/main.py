from fastapi import FastAPI
from .database import Base, engine
from .routers import auth_router, users, companies, payments, debug
from . import seed

Base.metadata.create_all(bind=engine)
seed.run()


app = FastAPI(title="AstraFinAPI", version="1.0.0")
app.include_router(auth_router.router)
app.include_router(users.router)
app.include_router(companies.router)
app.include_router(payments.router)
app.include_router(debug.router)

@app.get("/health")
def health():
    return {"status": "ok"}