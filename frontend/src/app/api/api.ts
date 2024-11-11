import axios from 'axios'
import { createAsyncThunk } from '@reduxjs/toolkit';

const host = "http://localhost:8000"

interface StreamResult {
  cypherResult: any; // Replace 'any' with the actual type of cypherResult
  langGraphResult: any[]; // Replace 'any[]' with the actual type of langGraphResult
}

export const getCurrNode = createAsyncThunk<StreamResult, string>(
  'node/getNodeAndStream',
  async (nodeName: string, { dispatch }) => {
    try {
      const response = await fetch(`${host}/getNodeAndStream?node_name=${nodeName}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.body) {
        throw new Error('Response body is not readable');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      return new Promise((resolve, reject) => {
        async function readStream() {
          let cypherResult = null;
          const langGraphResult = [];

          try {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              const chunk = decoder.decode(value, { stream: true });
              const lines = chunk.split('\n');

              for (const line of lines) {
                if (line.trim() === '') continue;
                const data = JSON.parse(line);
                if (data.type === 'cypher_result') {
                  cypherResult = data.result;
                } else if (data.type === 'folium_map' || data.type === 'plotly_map') {
                  langGraphResult.push(data.content);
                  const img = document.createElement('img');
                  img.src = `data:image/png;base64,${data.content}`;
                  document.body.appendChild(img);                
                }
              }
            }

            return { cypherResult, langGraphResult };
          } catch (error) {
            console.log(error);
            reject(error);
          }
        }
        readStream();
      });
    } catch (error) {
      console.log(error);
      throw error;
    }
  }
);

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