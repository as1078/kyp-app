def lc_retrieval_query(top_chunks = 5,
        top_communities = 3,
        top_outside_rels = 10,
        top_inside_rels = 10
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
    // We don't have covariates or claims here
    RETURN {{
        Chunks: text_mapping, Reports: report_mapping, 
        Relationships: [rel IN (outsideRels + insideRels) | rel.descriptionText], 
        Entities: [entity IN entities | entity.descriptionText]
        }} AS text, 1.0 AS score,
        {{
            EntityData: entities,
            RelationshipsData: outsideRels + insideRels
        }} AS metadata
    """