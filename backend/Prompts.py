def lc_retrieval_query(top_chunks = 5,
        top_communities = 3,
        top_outside_rels = 10,
        top_inside_rels = 10,
        top_documents=10
):
    return f"""
    WITH collect(node) as nodes
    // Entity - Text Unit Mapping
    WITH
    collect {{
        UNWIND nodes as n
        MATCH (n)<-[:HAS_ENTITY]->(c:__Chunk__)
        WITH c, count(distinct n) as freq
        RETURN c.text AS chunkText
        ORDER BY freq DESC
        LIMIT {top_chunks}
    }} AS text_mapping,
    // Document Mapping
    collect {{
        UNWIND nodes as n
        MATCH (n)<-[:HAS_ENTITY]->(c:__Chunk__)-[:PART_OF]->(d:__Document__)
        WITH d, count(distinct n) as freq
        RETURN d
        ORDER BY freq DESC
        LIMIT {top_documents}
    }} AS document_mapping,
    // Entity - Report Mapping
    collect {{
        UNWIND nodes as n
        MATCH (n)-[:IN_COMMUNITY]->(c:__Community__)
        WITH c, c.rank as rank, c.weight AS weight
        RETURN c.summary 
        ORDER BY rank, weight DESC
        LIMIT {top_communities}
    }} AS report_mapping,
    // Outside Relationships 
    collect {{
        UNWIND nodes as n
        MATCH (n)-[r:RELATED]-(m) 
        WHERE NOT m IN nodes
        RETURN {{ 
            descriptionText: r.description,
            type: type(r),
            entityName1: n.name,
            entityName2: m.name
          }} as rel
        ORDER BY r.rank, r.weight DESC 
        LIMIT {top_outside_rels}
    }} as outsideRels,
    // Inside Relationships 
    collect {{
        UNWIND nodes as n
        MATCH (n)-[r:RELATED]-(m) 
        WHERE m IN nodes
        RETURN {{
            descriptionText: r.description,
            type: type(r),
            entityName1: n.name,
            entityName2: m.name
        }} as rel
        ORDER BY r.rank, r.weight DESC 
        LIMIT {top_inside_rels}
    }} as insideRels,
    // Entities description
    collect {{
        UNWIND nodes as n
        RETURN {{
            descriptionText: n.description,
            name: n.name
        }} as entity
    }} as entities
    RETURN {{
        Chunks: text_mapping, Reports: report_mapping, 
        Relationships: [rel IN (outsideRels + insideRels) | rel.descriptionText], 
        Entities: [entity IN entities | entity.descriptionText]
        }} AS text, 1.0 AS score,
        {{
            EntityData: entities,
            RelationshipsData: outsideRels + insideRels,
            Documents: document_mapping
        }} AS metadata
    """

custom_prompt_template = """
Use the following pieces of information to answer the user's question. Be concise and only use the given information to answer. If you can't answer the question based on the information, say "I don't have enough information to answer that."

Context: {context}

Question: {question}

Answer:
"""

def node_click_cypher_query(query, top_docs=100):
    return f"""
    MATCH (e:__Entity__)
    WHERE e.name = '{query}'
    MATCH (e)<-[:HAS_ENTITY]-(c:__Chunk__)-[:PART_OF]->(d:__Document__)
    WITH e, d
    ORDER BY d.fatalities DESC
    WITH e, collect(DISTINCT d)[0..{top_docs}] AS limited_docs
    RETURN
        labels(e) AS entity_labels,
        e.name AS entity_name,
        e.description AS entity_description,
        e.type AS entity_type,
        limited_docs AS associated_documents
"""