import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { getCurrNode } from '../api/api'

// Define a type for the slice state
interface NodeState {
  labels: String[],
  name: String,
  description: String,
  type: String,
  status: String
}

// Define the initial state using that type
const initialState: NodeState = {
  labels: [],
  name: '',
  description: '',
  type: '',
  status: 'idle'
}

export const nodeSlice = createSlice({
  name: 'counter',
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
        state.labels = action.payload.labels;
        state.name = action.payload.name;
        state.description = action.payload.description;
        state.type = action.payload.type;
      })
      .addCase(getCurrNode.rejected, (state, action) => {
        state.status = 'failed';
        //state.error = action.error.message;
      });
  }
})

// Other code such as selectors can use the imported `RootState` type
//export const selectCount = (state: RootState) => state.counter.value

export default nodeSlice.reducer