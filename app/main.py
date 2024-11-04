from fastapi import FastAPI
from app.routes.user import user_route

def create_application():
    application = FastAPI()
    return application


app = create_application()


@app.get("/")
async def root():
    return {"message": "Hi, I am Describly. Awesome - Your setrup is done & working."}


app.include_router(user_route)