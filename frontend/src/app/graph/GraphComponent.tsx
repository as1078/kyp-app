import React, { useEffect, useRef, useState } from 'react';
import { Network } from "vis-network";
import { createGraph } from './CreateGraph';
import { RelationshipMetadata, NodeData, EdgeData } from "./GraphData"
import { getCurrNode } from '../api/api'
import { useDispatch } from 'react-redux';
import { useRouter } from "next/navigation"
import { AppDispatch } from "../store/store"
import RelationDialog from "./RelationDialog"
import { FullItem } from "vis-data/declarations/data-interface";

interface GraphComponentProps {
  metadata: RelationshipMetadata[];
  entityData: NodeData;
}


const GraphComponent: React.FC<GraphComponentProps> = ({ metadata, entityData }) => {
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<Network | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<FullItem<EdgeData, "id"> | null>();
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);

  const handleCloseDialog = () => {
    console.log("handleCloseDialog called");
    setSelectedEdge(null);
    if (selectedEdgeId && networkRef.current) {
      networkRef.current.updateEdge(selectedEdgeId, { width: 1 }); // Reset to normal width
      setSelectedEdgeId(null);
    }
  };

  useEffect(() => {
    console.log("useEffect ran");

    console.log("Selected Edge value: " + !!selectedEdge)
  }, [selectedEdge])

  useEffect(() => {
    if (!containerRef.current) return;

    const { nodes, edges } = createGraph(metadata, entityData);

    const data = { nodes, edges };
    const options = {
      nodes: {
        shape: 'dot',
        size: 16,
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

    networkRef.current = network;
        
    network.on('click', function(params) {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        console.log(nodeId);
        dispatch(getCurrNode(nodeId))
        router.push(`/${nodeId}`)
      } else if (params.edges.length > 0) {
        const edgeId = params.edges[0];
        const edge = edges.get(edgeId);
        if (edge) {
          //@ts-ignore
          setSelectedEdge(edge)
          setSelectedEdgeId(edgeId);
          network.updateEdge(edgeId, { width: 2 });
        }
      }
    });
    network.on('hoverNode', (node) => {
      const container = containerRef?.current
      if (container) {
        container.style.cursor = 'pointer';
      }
    })

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
      }
    };
  }, [metadata, entityData]);


  return(
    <div>
      <div ref={containerRef} style={{ height: '600px', width: '100%' }}/>;
      {selectedEdge && <RelationDialog edge={selectedEdge} onClose={handleCloseDialog}/>}
    </div>

  ) 
};


export default GraphComponent;
