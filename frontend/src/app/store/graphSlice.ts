import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { getGraphData } from '../api/api'
import { NodeData, RelationshipMetadata } from '../graph/GraphData'


interface GraphState {
  query: string;
  answer: string,
  entityData: NodeData | null,
  graphData: RelationshipMetadata[]
  status: string
}

const initialState: GraphState = {
  query: '',
  answer: '',
  entityData: null,
  graphData: [],
  status: 'idle'
}


export const graphSlice = createSlice({
  name: 'graph',
  // `createSlice` will infer the state type from the `initialState` argument
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(getGraphData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getGraphData.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.answer = action.payload.answer;
        state.query = action.payload.query;
        const entityData = action.payload.metadata.EntityData;
        const firstEntity = entityData[0]
        state.entityData = new NodeData("1", firstEntity.name)
        const relationshipsData = action.payload.metadata.RelationshipsData;
        const parsedMetadata: RelationshipMetadata[] = relationshipsData.map((item: any) => ({
          descriptionText: item.descriptionText,
          entityName1: item.entityName1,
          entityName2: item.entityName2,
          type: item.type
        }));
        state.graphData = parsedMetadata;

      })
      .addCase(getGraphData.rejected, (state, action) => {
        state.status = 'failed';
        //state.error = action.error.message;
      });
  }
})

// Other code such as selectors can use the imported `RootState` type
//export const selectCount = (state: RootState) => state.counter.value

export default graphSlice.reducer