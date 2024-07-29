from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from typing import List
import openai
import io
import sys
import uuid
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.graphs.graph_document import GraphDocument
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from config import settings
import Prompts
from langchain.chains import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

#from neo4j import GraphDatabase


class VectorDB():
    def __init__(self):
 
        openai.api_key = settings.OPENAI_API_KEY
        self.neo4j_url = settings.NEO4J_URL
        self.neo4j_user = settings.NEO4J_USER
        self.neo4j_password = settings.NEO4J_PASSWORD
        self.graph = Neo4jGraph(url=self.neo4j_url, username=self.neo4j_user, password=self.neo4j_password)
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=openai.api_key)
        self.llm_transformer = LLMGraphTransformer(
            llm=self.llm,
            node_properties=["description"],
            relationship_properties=["description"]
        )
        self.qa_prompt = PromptTemplate(
    input_variables=["context", "question"], template=Prompts.CYPHER_QA_TEMPLATE
)
        self.cypher_prompt = PromptTemplate(
    template = Prompts.cypher_generation_template,
    input_variables = ["schema", "question"]
)

    def read_data_from_pdf(self, file_content: bytes):
        print("reading data from pdf...")
        text = ""
        buffer = io.BytesIO(file_content)
        pdf_reader = PdfReader(buffer)
        for page in pdf_reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text
        return text

    def get_text_chunks(self, text: str):
        print("getting text chunks ...")
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=300,
            chunk_overlap=100,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks
    
    def process_text(self, text: str, document_id: str) -> List[GraphDocument]:
        doc = Document(page_content=text, metadata={"document_id": document_id})
        return self.llm_transformer.convert_to_graph_documents([doc])

    
    def upload_pdf(self, filename: str):
        raw_text = self.read_data_from_pdf(filename)
        chunks = self.get_text_chunks(raw_text)
        document_id = str(uuid.uuid4())
        graph_documents = self.process_text(chunks, document_id)
        self.graph.add_graph_documents(
            [graph_documents],
            baseEntityLabel=True,
            include_source=True
        )
    
    
    def query_graph(self, user_input):
        chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True,
            return_intermediate_steps=True,
            cypher_prompt=self.cypher_prompt,
            qa_prompt=self.qa_prompt
        )
        print("User input: " + user_input)
        result = chain.invoke(user_input)
        return result

    def entity_resolution():
        return None
    
            


        
