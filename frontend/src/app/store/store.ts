'use client'

import { configureStore, combineReducers } from '@reduxjs/toolkit'
import nodeSliceReducer from "./nodeSlice"
import graphSliceReducer from "./graphSlice"
import { persistStore, persistReducer } from 'redux-persist';
import { FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } from 'redux-persist';
import storageSession from 'redux-persist/lib/storage/session'

const persistConfig = {
  key: 'root',
  storage: storageSession,
  whitelist: ['node', 'graph'], // only user will be persisted
};

const rootReducer = combineReducers({
  node: nodeSliceReducer,
  graph: graphSliceReducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
  
})

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>

export type AppDispatch = typeof store.dispatch