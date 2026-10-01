import { configureStore } from "@reduxjs/toolkit";
import maintenanceReducer from "./maintenanceSlice";

export const store = configureStore({
  reducer: {
    maintenance: maintenanceReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
