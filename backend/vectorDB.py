from typing import List
import openai
import math
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from config import settings
from neo4j import GraphDatabase
from Prompts import lc_retrieval_query, node_click_cypher_query
from db import EntityNode, DocumentNode, LangGraphInput
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
                    OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai.api_key),
                    url=self.neo4j_url,
                    username=self.neo4j_user,
                    password=self.neo4j_password,
                    index_name="entity",
                    retrieval_query=self.lc_retrieval_query
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
                        llm=self.llm,
                        retriever=self.lc_vector.as_retriever(),
                        return_source_documents=True,
                        verbose = True,
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
        metadata = source.metadata
        #documents = metadata['Documents']
        filtered_result = {
            'EntityData': metadata.get('EntityData', []),
            'RelationshipsData': metadata.get('RelationshipsData', [])
        }
        print(filtered_result)
        # Retrieve documents from metadata so graph agent can make graphs
        return (response["result"], filtered_result)

    def process_entity(self, result):
        print(result['entity_labels'])
        print(result['entity_name'])
        print(result['entity_description'])
        return EntityNode(
            labels = result["entity_labels"],
            name = result["entity_name"],
            description = result["entity_description"],
            type = result["entity_type"],
        )
    
    def process_document(self, documents):
        print("processing document...", documents)
        return DocumentNode(
            country = documents['country'],
            geo_precision = documents['geo_precision'],
            disorder_type = documents['disorder_type'],
            latitude = documents['latitude'],
            admin = documents['admin'],
            title = documents['title'],
            civilian_targeting = documents['civilian_targeting'] == 'Civilian targeting',
            sub_event_type = documents['sub_event_type'],
            actor2 = documents['actor2'] if isinstance(documents['actor2'], str) else "",
            actor1 = documents['actor1'],
            event_type = documents['event_type'],
            interaction = documents['interaction'],
            time_precision = documents['time_precision'],
            location = documents['location'],
            id = documents['id'],
            fatalities = documents['fatalities'],
            region = documents['region'],
            timestamp = documents['timestamp'],
            longitude = documents['longitude'],
        )
    
    def retrieve_node_data(self, user_input):
        node_prompt = node_click_cypher_query(user_input)
        cypher_results = self.db_query(node_prompt)
        return cypher_results

    def prep_lang_graph_input(self, cypher_results) -> LangGraphInput:
        print("Preparing Lang Graph input...")
        entity_data = self.process_entity(cypher_results)
        doc_data = []
        associated_documents = cypher_results["associated_documents"]
        for result in associated_documents:
            doc_data.append(self.process_document(result))
        graph_input = LangGraphInput(entities=entity_data, documents=doc_data)
        return graph_input