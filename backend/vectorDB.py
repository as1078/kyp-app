from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from typing import List
import openai
import io
import uuid
from qdrant_client.http.models import PointStruct
from qdrant_client import QdrantClient, models
from config import settings
from qdrant_client.models import VectorParams, Distance
import Prompts
import json
from neo4j import GraphDatabase


class VectorDB():
    def __init__(self):
        self.qdrant_client = QdrantClient(
            url=settings.QDRANT_URL, 
            api_key=settings.QDRANT_API_KEY,
        )
        openai.api_key = settings.OPENAI_API_KEY
        neo4j_url = settings.NEO4J_URL
        neo4j_user = settings.NEO4J_USER
        neo4j_password = settings.NEO4J_PASSWORD
        self.gds = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))

        # self.qdrant_client.create_collection(
        #     collection_name="1536_entities",
        #     vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        #             optimizers_config=models.OptimizersConfigDiff(
        #                 indexing_threshold=0,
        #             ),
        # )

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
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks
    
    def get_embedding(self, text_chunks: List[str], model_id="text-embedding-ada-002"):
        print("creating embeddings ...")
        points = []
        for idx, chunk in enumerate(text_chunks):
            response = openai.Embedding.create(
                input=chunk,
                model=model_id
            )
            embeddings = response['data'][0]['embedding']
            exists = self.find_embedding(embeddings)
            if exists:
                return None
            point_id = str(uuid.uuid4())
            points.append(PointStruct(id=point_id, vector=embeddings,payload={"text": chunk}))
        return points
    
    def find_embedding(self, embeddings: List[float], threshold=0.1)->bool:
        search_result = self.qdrant_client.search(
            collection_name="1536_entities",
            query_vector=embeddings,
            limit=1
        )
        print(search_result)
        if search_result and search_result[0].score > threshold:
            print("Similar document found")
            return True
        return False


    def insert_data(self, points: List[PointStruct]):
        print("inserting data into qdrant ...")
        operation_info = self.qdrant_client.upsert(
            collection_name="1536_entities",
            wait=True,
            points=points
        )
        return operation_info

    def create_answer_with_context(self, query: str):
        response = openai.Embedding.create(
            input=query,
            model="text-embedding-ada-002"
        )
        embeddings = response['d ata'][0]['embedding']

        search_result = self.qdrant_client.search(
            collection_name="1536_entities",
            query_vector=embeddings,
            limit=1
        )

        prompt = "Context:\n"
        for result in search_result:
            prompt += result.payload['text'] + "\n---\n"
        prompt += "Question:" + query + "\n---\n" + "Answer:"
        print("----PROMPT START----")
        print(":", prompt)
        print("----PROMPT END----")

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    
    def upload_pdf(self, filename: str):
        raw_text = self.read_data_from_pdf(filename)
        chunks = self.get_text_chunks(raw_text)
        vectors = self.get_embedding(chunks)
        if not vectors:
            return None
        operation_info = self.insert_data(vectors)
        return operation_info
    
    def get_entity_embedding(self, entity):
        response = openai.Embedding.create(
            input=entity,
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']
    
    def generate_cypher(self, json_object):
        e_statements = []
        r_statements = []

        e_label_map = {}
        for entity in json_object['entities']:
            label = entity['type']
            id = entity['name']
            id = id.replace("-", "").replace("_", "")
            properties = {k: v for k, v in entity.items() if k not in ["name", "type"]}
            cypher = f'MERGE (n:{label} {{id: "{id}"}})'
            if properties:
                props_str = ", ".join(
                    [f'n.{key} = "{val}"' for key, val in properties.items()]
                )
                cypher += f" ON CREATE SET {props_str}"
            e_statements.append(cypher)
            e_label_map[id] = label

            for rs in json_object['relationships']:
                src_id, rs_type, tgt_id = rs['source'], rs['relation'], rs['target']
                src_id = src_id.replace("-", "").replace("_", "")
                tgt_id = tgt_id.replace("-", "").replace("_", "")
                src_label = e_label_map[src_id]
                tgt_label = e_label_map[tgt_id]

                cypher = f'MERGE (a:{src_label} {{id: "{src_id}"}}) MERGE (b:{tgt_label} {{id: "{tgt_id}"}}) MERGE (a)-[:{rs_type}]->(b)'
                r_statements.append(cypher)
        return e_statements + r_statements
    
    def ner(self, text_chunks: List[str]):
        prompt = Prompts.ner
        for idx, chunk in enumerate(text_chunks):
            curr_prompt = prompt + chunk
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": curr_prompt}
                ]
            )
            result = completion.choices[0].message.content
            json_result = json.loads(result)
            cypher_statements = self.generate_cypher(json_result)
            for stmt in cypher_statements:
                try:
                    self.gds.execute_query(stmt)
                except Exception as e:
                    print(f"Error executing statement: {stmt}. Error: {e}")
            


        
