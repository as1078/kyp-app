import { createSlice } from '@reduxjs/toolkit'
import { getCurrNode, updateCypherResult } from '../api/api'

// Define a type for the slice state
interface EntityData {
  labels: String[] | null,
  name: String,
  description: String,
  type: String,
}

// Type for image in S3
interface ImageData {
  filename: string
  url: string
}

interface EntityImageData {
  entity: EntityData
  image: ImageData
  status: 'idle' | 'loading' | 'succeeded' | 'cypher_succeeded' | 'failed';
  error: String | null
}

const initialEntity: EntityData = {
  labels: [],
  name: '',
  description: '',
  type: '',
}

const initialImage: ImageData = {
  filename: '',
  url: '',
}
const initialState: EntityImageData = {
  entity: initialEntity,
  image: initialImage,
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
    .addCase(updateCypherResult, (state, action) => {
      // Update state with cypher result
      state.status = 'cypher_succeeded';
      const { labels, name, description, type } = action.payload;
      Object.assign(state.entity, { labels, name, description, type });
    })
      .addCase(getCurrNode.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(getCurrNode.fulfilled, (state, action) => {
        state.status = 'succeeded';
        const { s3_key, url } = action.payload.langGraphResult.content;
      
        Object.assign(state.image, { filename: s3_key, url });
      })
      .addCase(getCurrNode.rejected, (state, action) => {
        state.status = 'failed';
      });
  }
})

// Other code such as selectors can use the imported `RootState` type
//export const selectCount = (state: RootState) => state.counter.value

export default nodeSlice.reducer