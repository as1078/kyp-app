'use client'

import { configureStore } from '@reduxjs/toolkit'
import nodeSliceReducer from "./nodeSlice"
// ...

export const store = configureStore({
  reducer: {
    node: nodeSliceReducer
  },
})


export type RootState = ReturnType<typeof store.getState>

export type AppDispatch = typeof store.dispatch