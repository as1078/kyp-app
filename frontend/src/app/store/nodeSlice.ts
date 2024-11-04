import { createSlice } from '@reduxjs/toolkit'
import { getCurrNode } from '../api/api'

// Define a type for the slice state
interface NodeData {
  labels: String[],
  name: String,
  description: String,
  type: String,
  status: String
}

interface NodeState {
  nodes: NodeData[];
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

const initialState: NodeState = {
  nodes: [],
  status: 'idle',
  error: null
}

export const nodeSlice = createSlice({
  name: 'node',
  // `createSlice` will infer the state type from the `initialState` argument
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(getCurrNode.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getCurrNode.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.nodes = action.payload.cypherResult.map((node: any) => ({
          labels: node.labels || [],
          name: node.name || '',
          description: node.description || '',
          type: node.type || ''
        }));
      })
      .addCase(getCurrNode.rejected, (state, action) => {
        state.status = 'failed';
      });
  }
})

// Other code such as selectors can use the imported `RootState` type
//export const selectCount = (state: RootState) => state.counter.value

export default nodeSlice.reducer