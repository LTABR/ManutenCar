import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type {
  CarType,
  FrequencyType,
  MaintenanceStateType,
  TrackedPartType,
} from "../types/maintenance";

const initialState: MaintenanceStateType = {
  cars: [
    {
      id: "car-1",
      model: "",
      distance: "250",
      frequency: "week",
      parts: [],
    },
  ],
  activeCarId: "car-1",
  selectedPart: "",
  formError: "",
};

const maintenanceSlice = createSlice({
  name: "maintenance",
  initialState,
  reducers: {
    addCar(state, action: PayloadAction<CarType>) {
      state.cars.push(action.payload);
      state.activeCarId = action.payload.id;
      state.selectedPart = "";
      state.formError = "";
    },
    selectCar(state, action: PayloadAction<string>) {
      if (state.cars.some((car) => car.id === action.payload)) {
        state.activeCarId = action.payload;
        state.selectedPart = "";
        state.formError = "";
      }
    },
    setModel(state, action: PayloadAction<string>) {
      const car = state.cars.find((item) => item.id === state.activeCarId);
      if (car) car.model = action.payload;
    },
    setDistance(state, action: PayloadAction<string>) {
      const car = state.cars.find((item) => item.id === state.activeCarId);
      if (car) car.distance = action.payload;
    },
    setFrequency(state, action: PayloadAction<FrequencyType>) {
      const car = state.cars.find((item) => item.id === state.activeCarId);
      if (car) car.frequency = action.payload;
    },
    setSelectedPart(state, action: PayloadAction<string>) {
      state.selectedPart = action.payload;
      state.formError = "";
    },
    setFormError(state, action: PayloadAction<string>) {
      state.formError = action.payload;
    },
    addPart(
      state,
      action: PayloadAction<{ carId: string; part: TrackedPartType }>,
    ) {
      const car = state.cars.find((item) => item.id === action.payload.carId);
      if (
        !car ||
        car.parts.some((part) => part.partId === action.payload.part.partId)
      )
        return;
      car.parts.push(action.payload.part);
      state.selectedPart = "";
      state.formError = "";
    },
    updatePartDate(
      state,
      action: PayloadAction<{ carId: string; id: string; lastServiced: string }>,
    ) {
      const car = state.cars.find((item) => item.id === action.payload.carId);
      const part = car?.parts.find((item) => item.id === action.payload.id);
      if (part) part.lastServiced = action.payload.lastServiced;
    },
    removePart(state, action: PayloadAction<{ carId: string; id: string }>) {
      const car = state.cars.find((item) => item.id === action.payload.carId);
      if (car)
        car.parts = car.parts.filter((part) => part.id !== action.payload.id);
    },
  },
});

export const {
  addCar,
  addPart,
  removePart,
  selectCar,
  setDistance,
  setFormError,
  setFrequency,
  setModel,
  setSelectedPart,
  updatePartDate,
} = maintenanceSlice.actions;

export default maintenanceSlice.reducer;
