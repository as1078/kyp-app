import axios from 'axios'
import { createAsyncThunk } from '@reduxjs/toolkit';

const host = "http://localhost:8000"

export const getCurrNode = createAsyncThunk(
    'node/getCurrNode',
    async (nodeName: String, thunkAPI) => {
      try {
        const response = await axios.get(host + `/getNode?node_name=${nodeName}`)
        console.log(response)
        return response.data.result;
    } catch (error: any) {
        return thunkAPI.rejectWithValue(error.response.data);
    }
  });

  export const getGraphData = createAsyncThunk(
    'graph/getGraphData',
    async (searchQuery: string, thunkAPI) => {
      try {
        const response = await axios.get(host + `/search?query=${searchQuery}`)
        console.log(response)
        return response.data
      } catch (error: any) {
        return thunkAPI.rejectWithValue(error.response.data);
      }
    }
  )