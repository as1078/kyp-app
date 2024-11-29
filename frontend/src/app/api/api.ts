import axios from 'axios'
import { createAsyncThunk, createAction } from '@reduxjs/toolkit';

const host = "http://localhost:8000"

interface StreamResult {
  cypherResult: any; // Replace 'any' with the actual type of cypherResult
  langGraphResult: {
    type: string;
    content: {
      s3_key: string;
      url: string;
    }
  }
}

// Create a separate action for updating cypher result
export const updateCypherResult = createAction<any>('node/updateCypherResult');

export const getCurrNode = createAsyncThunk<StreamResult, string>(
  'node/getNodeAndStream',
  async (nodeName: string, { dispatch }) => {
    try {
      const response = await fetch(`${host}/getNodeAndStream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ node_name: nodeName }),
      });

      if (!response.body) {
        throw new Error('Response body is not readable');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      return new Promise<StreamResult>(async (resolve, reject) => {
        async function readStream() {
          let cypherResult = null;
          let langGraphResult = null;
          try {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              const chunk = decoder.decode(value, { stream: true });
              const lines = chunk.split('\n');

              for (const line of lines) {
                console.log("Line: " + line);
                if (line.trim() === '') continue;
                const data = JSON.parse(line);
                if (data.type === 'cypher_result') {
                  cypherResult = data.content;
                  dispatch(updateCypherResult(cypherResult));
                } else if (data.type === 'folium_map' || data.type === 'plotly_map') {
                  langGraphResult = data.content;            
                } else if (data.type === 'error') {
                  console.log(data.content);
                  reject(data.content);
                }
              }
            }

            return { cypherResult, langGraphResult };
          } catch (error) {
            console.log(error);
            reject(error);
          }
        }
        const result = await readStream()
        resolve(result ?? { cypherResult: null, langGraphResult: null });
      });
    } catch (error) {
      console.log(error);
      throw error;
    }
  }
);

// Separate function to load images from URLs
export const loadImageFromUrl = async (url: string): Promise<string> => {
  try {
    const response = await fetch(url);
    const blob = await response.blob();
    return URL.createObjectURL(blob);
  } catch (error) {
    console.error('Error loading image:', error);
    throw error;
  }
};

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