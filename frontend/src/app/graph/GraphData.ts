export interface RelationshipMetadata {
    descriptionText: string;
    entityName1: string;
    entityName2: string;
    type: string;
  }
  
export interface NodeData {
  id: string;
  label: string;
  color?: string;  // Optional color property
}
  
export interface EdgeData {
  id: number;
  from: string;
  to: string;
  description: string;
}
  