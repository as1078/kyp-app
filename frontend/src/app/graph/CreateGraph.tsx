import { DataSet } from "vis-data";
import { RelationshipMetadata, NodeData, EdgeData } from "./GraphData"


export function createGraph(metadata: RelationshipMetadata[], entityData: NodeData) {
    const nodes = new DataSet<NodeData>();
    const edges = new DataSet<EdgeData>();
    const nodeSet = new Set<string>();
  
    metadata.forEach((item, index) => {
      if (!nodeSet.has(item.entityName1)) {
        nodes.add({ id: item.entityName1, label: item.entityName1, color: entityData.label === item.entityName1 ? '#FF5733' : '#4CAF50' });
        nodeSet.add(item.entityName1);
      }
      if (!nodeSet.has(item.entityName2)) {
        nodes.add({ id: item.entityName2, label: item.entityName2, color: entityData.label === item.entityName2 ? '#FF5733' : '#4CAF50' });
        nodeSet.add(item.entityName2);
      }
  
      edges.add({
        id: index,
        from: item.entityName1,
        to: item.entityName2,
        title: item.descriptionText
      });
    });
  
    return { nodes, edges };
  }
