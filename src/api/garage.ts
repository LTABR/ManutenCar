import { apiRequest } from "./client";
import type { CarType, TrackedPartType } from "../types/maintenance";

/**
 * REST contract for a signed-in user's garage.
 * All calls automatically include the JWT set by auth.login().
 */
export const garageApi = {
  listCars: () => apiRequest<CarType[]>("/cars"),

  createCar: (car: Omit<CarType, "id">) =>
    apiRequest<CarType>("/cars", {
      method: "POST",
      body: JSON.stringify(car),
    }),

  updateCar: (carId: string, changes: Partial<Omit<CarType, "id" | "parts">>) =>
    apiRequest<CarType>(`/cars/${encodeURIComponent(carId)}`, {
      method: "PATCH",
      body: JSON.stringify(changes),
    }),

  deleteCar: (carId: string) =>
    apiRequest<void>(`/cars/${encodeURIComponent(carId)}`, { method: "DELETE" }),

  addPart: (carId: string, part: Omit<TrackedPartType, "id">) =>
    apiRequest<TrackedPartType>(`/cars/${encodeURIComponent(carId)}/parts`, {
      method: "POST",
      body: JSON.stringify(part),
    }),

  updatePart: (
    carId: string,
    partId: string,
    changes: Partial<Omit<TrackedPartType, "id" | "partId">>,
  ) =>
    apiRequest<TrackedPartType>(
      `/cars/${encodeURIComponent(carId)}/parts/${encodeURIComponent(partId)}`,
      { method: "PATCH", body: JSON.stringify(changes) },
    ),

  deletePart: (carId: string, partId: string) =>
    apiRequest<void>(
      `/cars/${encodeURIComponent(carId)}/parts/${encodeURIComponent(partId)}`,
      { method: "DELETE" },
    ),
};
