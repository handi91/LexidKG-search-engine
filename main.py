from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from execute_query import generate_get_query_result
from mapping import generate_mapping
from autocomplete_suggestion import generate_autocomplete_suggestion

app = FastAPI()

mapping = None
get_query_result = None
get_autocomplete_suggestion = None
error_query_result = "error"
suggestion_task = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    global mapping, get_query_result, get_autocomplete_suggestion
    mapping = generate_mapping()
    get_query_result = generate_get_query_result()
    get_autocomplete_suggestion = generate_autocomplete_suggestion()

@app.get("/")
async def index():
    return {
        "code": 200
    }

@app.post("/suggestion")
async def get_suggestions(input: str):
    global suggestion_task

    if suggestion_task is not None:
        try:
            suggestion_task.cancel()
        except:
            pass
    suggestion_task = asyncio.create_task(get_autocomplete_suggestion_task(input))
    suggestions = await suggestion_task
    return {
        "suggestions": suggestions
    }

async def get_autocomplete_suggestion_task(input: str):
    suggestions = get_autocomplete_suggestion(input)
    return suggestions

@app.post("/ask")
async def get_answer(question: str):
    result = ""
    invalid = True
    query = mapping(question)
    if query:
        query_result = get_query_result(query)
        if query_result != error_query_result:
            invalid = False
            result = query_result
    return {
        "invalid": invalid,
        "result": result 
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080,
                log_level="info", reload=True)