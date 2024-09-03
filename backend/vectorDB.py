from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from typing import List
import openai
import io
import pandas as pd
import uuid
from langchain_core.documents import Document
from langchain_community.graphs.graph_document import GraphDocument
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from config import settings
from neo4j import GraphDatabase, Result
from Prompts import lc_retrieval_query, custom_prompt_template, node_click_cypher_query
from langchain_core.runnables import RunnableLambda
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Neo4jVector
from langchain.chains import RetrievalQA
from typing import Dict, Any




class VectorDB():
    def __init__(self):
 
        openai.api_key = settings.OPENAI_API_KEY
        self.neo4j_url = settings.NEO4J_URL
        self.neo4j_user = settings.NEO4J_USER
        self.neo4j_password = settings.NEO4J_PASSWORD
        self.driver = GraphDatabase.driver(self.neo4j_url, auth=(self.neo4j_user, self.neo4j_password))
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=openai.api_key)
        self.lc_retrieval_query = lc_retrieval_query()
        self.lc_vector = Neo4jVector.from_existing_index(
                    OpenAIEmbeddings(model="text-embedding-3-small"),
                    url=self.neo4j_url,
                    username=self.neo4j_user,
                    password=self.neo4j_password,
                    index_name="entity",
                    retrieval_query=self.lc_retrieval_query)
        CUSTOM_PROMPT = PromptTemplate(
            template=custom_prompt_template, input_variables=["context", "question"]
        )
        self.qa_chain = RetrievalQA.from_chain_type(
                        llm=self.llm,
                        retriever=self.lc_vector.as_retriever(),
                        return_source_documents=True,
                        verbose = True,
        )
    
    def inspect(self, state):
        """Print the state passed between components in the chain"""
        print("\n======== Intermediate State ========")
        print(state)
        print("====================================\n")
        return state

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
    
    def db_query(self, cypher: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
        result = self.driver.execute_query(
                    cypher, 
                    parameters_=params, 
                    result_transformer_=lambda result: [dict(record) for record in result]
        )
        return result[0]
        
    
    def query_graph(self, user_input):
        print("User input: " + user_input)
        response = self.qa_chain.invoke({"query": user_input})
        source = response.get('source_documents', [])[0]
        print(response)
        metadata = source.metadata
        #relationships_data = metadata['RelationshipsData']
        #return (response["result"], relationships_data)
        return (response["result"], metadata)
    
    def retrieve_node_data(self, user_input):
        node_prompt = node_click_cypher_query
        result = self.db_query(node_prompt, {"query": user_input})
        return result

    def entity_resolution():
        return None
    
            


        
