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
    replaceCars(state, action: PayloadAction<CarType[]>) {
      state.cars = action.payload;
      state.activeCarId = action.payload[0]?.id ?? "";
      state.selectedPart = "";
      state.formError = "";
    },
    replaceCar(state, action: PayloadAction<CarType>) {
      const carIndex = state.cars.findIndex(
        (car) => car.id === action.payload.id,
      );
      if (carIndex >= 0) state.cars[carIndex] = action.payload;
    },
    addCar(state, action: PayloadAction<CarType>) {
      state.cars.push(action.payload);
      state.activeCarId = action.payload.id;
      state.selectedPart = "";
      state.formError = "";
    },
    removeCar(state, action: PayloadAction<string>) {
      const carIndex = state.cars.findIndex((car) => car.id === action.payload);
      if (carIndex < 0) return;
      state.cars.splice(carIndex, 1);
      state.activeCarId =
        state.activeCarId === action.payload
          ? state.cars[Math.min(carIndex, state.cars.length - 1)]?.id ?? ""
          : state.activeCarId;
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
    replacePart(
      state,
      action: PayloadAction<{ carId: string; part: TrackedPartType }>,
    ) {
      const car = state.cars.find((item) => item.id === action.payload.carId);
      const partIndex = car?.parts.findIndex(
        (item) => item.id === action.payload.part.id,
      );
      if (car && partIndex !== undefined && partIndex >= 0) {
        car.parts[partIndex] = action.payload.part;
      }
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
  removeCar,
  selectCar,
  setDistance,
  setFormError,
  setFrequency,
  setModel,
  setSelectedPart,
  replacePart,
  replaceCar,
  replaceCars,
} = maintenanceSlice.actions;

export default maintenanceSlice.reducer;
