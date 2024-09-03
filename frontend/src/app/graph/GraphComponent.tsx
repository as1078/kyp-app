import React, { useEffect, useRef } from 'react';
import { Network } from "vis-network";
import { createGraph } from './CreateGraph';
import { RelationshipMetadata, NodeData } from "./GraphData"
import { onNodeClick } from '../api/api'
import { useRouter } from "next/navigation"

interface GraphComponentProps {
  metadata: RelationshipMetadata[];
  entityData: NodeData;
}


const GraphComponent: React.FC<GraphComponentProps> = ({ metadata, entityData }) => {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const { nodes, edges } = createGraph(metadata, entityData);

    const data = { nodes, edges };
    const options = {
      nodes: {
        shape: 'dot',
        size: 16,
        cursor: 'pointer',
        chosen: {
          node: (values, id, selected, hovering) => {
            if (hovering) {
              values.cursor = 'pointer';
            }
          },
          label: function(values, id, selected, hovering) {
            // You can modify label properties here if needed
          }
        }
      },
      interaction: {
        hover: true
      },
      physics: {
        forceAtlas2Based: {
          gravitationalConstant: -26,
          centralGravity: 0.005,
          springLength: 230,
          springConstant: 0.18
        },
        maxVelocity: 146,
        solver: 'forceAtlas2Based',
        timestep: 0.35,
        stabilization: { iterations: 150 }
      }
    };

    const network = new Network(containerRef.current, data, options);
    network.on('click', function(params) {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        onNodeClick(nodeId)
        router.push(`/${nodeId}`)
      }
    });

    return () => {
      network.destroy();
    };
  }, [metadata, entityData]);

  return <div ref={containerRef} style={{ height: '600px', width: '100%' }} />;
};

export default GraphComponent;
