from fastapi import FastAPI, Request, Response, File, UploadFile
from fastapi.responses import JSONResponse
from vectorDB import VectorDB
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

vectorDB = VectorDB()

origins = [
    "http://localhost:5173",  # Adjust this to the URL/port of your React app
    "http://127.0.0.1:5173",  # Include any other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


## UPLOAD A PARGRAPH AND STORE INTO DB
@app.post('/uploadParagraph')
async def upload_paragraph(file: UploadFile = File(...)):

    if not file.filename.endswith('.pdf'):
        return JSONResponse(content={"error": "Invalid file format, expected a PDF."}, status_code=400)

    content = await file.read()
    operation_info = vectorDB.upload_pdf(content)
    await file.close()
    if not operation_info:
        return JSONResponse(content={"error": "Document already exists"}, status_code=500)
    print(operation_info)
    return JSONResponse(content={"success": "success"}, status_code=200)

@app.get('/search')
def search(query: str):
    print(f"Received query: {query}")
    answer, metadata = vectorDB.query_graph(query)
    print(answer)
    if not answer:
        return JSONResponse(content={'error': 'We were unable to generate an answer for the query'}, status_code=500)
    return JSONResponse(content={'answer': answer, 'metadata': metadata}, status_code=200)


@app.get("/")
async def root():
    return {"message": "Hello World"}