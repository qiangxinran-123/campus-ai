from fastapi import FastAPI

app = FastAPI(title="CampusAI API")


@app.get("/hello")
def hello():
    return {
        "message": "Hello, CampusAI!",
        "status": "ok"
    }