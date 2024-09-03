export interface RelationshipMetadata {
    descriptionText: string;
    entityName1: string;
    entityName2: string;
    type: string;
  }
  
  export class NodeData {
    id: string;
    label: string;
    color?: string;  // Optional color property

    constructor(id: string, label: string, color?: string) {
        this.id = id;
        this.label = label;
        this.color = color;
    }
}
  
  export interface EdgeData {
    id: number;
    from: string;
    to: string;
    title: string;
  }
  