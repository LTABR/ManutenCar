export type PartColorType =
  | "orange"
  | "blue"
  | "green"
  | "red"
  | "purple"
  | "yellow"
  | "teal"
  | "pink"
  | "slate";

export type PartType = {
  id: string;
  name: string;
  intervalKm: number;
  intervalMonths: number;
  category: string;
  color: PartColorType;
};

export type TrackedPartType = {
  id: string;
  partId: string;
  lastServiced: string;
};

export type FrequencyType = "week" | "month" | "year";

export type CarType = {
  id: string;
  model: string;
  distance: string;
  frequency: FrequencyType;
  parts: TrackedPartType[];
};

export type MaintenanceStateType = {
  cars: CarType[];
  activeCarId: string;
  selectedPart: string;
  formError: string;
};
