from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from vectorDB import VectorDB
from fastapi.middleware.cors import CORSMiddleware
from langgraph.lang_graph import LangGraph

app = FastAPI()
vectorDB = VectorDB()
lang_graph = LangGraph()

origins = [
    "http://localhost:5173",  # Adjust this to the URL/port of your React app
    "http://localhost:3000",  # Include any other origins as needed
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
    print(f"Answer: {answer}")
    if not answer:
        return JSONResponse(content={'error': 'We were unable to generate an answer for the query'}, status_code=500)
    return JSONResponse(content={'answer': answer, 'metadata': metadata, 'query': query}, status_code=200)

@app.get("/getNodeAndStream")
async def get_node(node_name: str):
    try:
        db_result = vectorDB.retrieve_node_data(node_name)
        lang_graph_input = vectorDB.prep_lang_graph_input(db_result)

        async def event_generator():
            yield JSONResponse(content={'type': 'cypher_result', 'result': lang_graph_input.entities})
        
            async for event in lang_graph.stream_events(lang_graph_input):
                if event.get('type') == 'folium_map':
                    yield JSONResponse(content={
                        'type': 'folium_map',
                        'content': event['content'],
                    })
                elif event.get('type') == 'plotly_map':
                    yield JSONResponse(content={'type': 'plotly_map', 'content': event['content']})
        return StreamingResponse(event_generator(), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Hello World"}