from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn
from execute_query import generate_get_query_result
from mapping import generate_mapping
from autocomplete_suggestion import generate_autocomplete_suggestion
from alternative_mapping import generate_alternative_mapping

app = FastAPI()

mapping = None
alternative_mapping = None
get_query_result = None
get_autocomplete_suggestion = None
error_query_result = "error"
not_found_query_result = "Jawaban tidak ditemukan"
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
    global mapping, get_query_result, get_autocomplete_suggestion, alternative_mapping
    mapping = generate_mapping()
    get_query_result = generate_get_query_result()
    get_autocomplete_suggestion = generate_autocomplete_suggestion()
    alternative_mapping = generate_alternative_mapping()

@app.get("/")
async def index():
    return {
        "code": 200
    }

@app.post("/suggestion")
async def get_suggestions(input: str, index: int, head: str, prev: str):
    suggestions = get_autocomplete_suggestion(input, index, head, prev)
    return {
        "suggestions": suggestions
    }

@app.post("/possible-answer")
async def get_answer_v2(question: str):
    result = ""
    query, question, q_index= alternative_mapping(question)
    print(query)
    if query:
        query_result = get_query_result(query, q_index)
        if query_result != error_query_result:
            result = query_result
    return {
        "question": question,
        "result": result 
    }

@app.post("/answer")
async def get_answer(question: str):
    result = ""
    invalid = True
    query, alt_query, q_index = mapping(question)
    print(query)
    if query != "":
        alt_result = get_query_result(alt_query, q_index) if alt_query else ''
        query_result = get_query_result(query, q_index)
        if query_result != error_query_result:
            invalid = False
            if alt_result != "":
                if query_result == not_found_query_result:
                    result = alt_result
                else:
                    result = query_result
            else:
                result = query_result 
    return {
        "invalid": invalid,
        "result": result 
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80,
                log_level="info", reload=True)