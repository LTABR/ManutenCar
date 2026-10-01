import type { PartType } from "../types/maintenance";

export const catalog: PartType[] = [
  { id: "engine-oil", name: "Engine oil & filter", intervalKm: 10000, intervalMonths: 12, category: "Engine", color: "orange" },
  { id: "air-filter", name: "Engine air filter", intervalKm: 20000, intervalMonths: 24, category: "Engine", color: "blue" },
  { id: "cabin-filter", name: "Cabin air filter", intervalKm: 15000, intervalMonths: 12, category: "Comfort", color: "green" },
  { id: "brake-fluid", name: "Brake fluid", intervalKm: 40000, intervalMonths: 24, category: "Brakes", color: "red" },
  { id: "brake-pads", name: "Brake pads", intervalKm: 40000, intervalMonths: 36, category: "Brakes", color: "purple" },
  { id: "spark-plugs", name: "Spark plugs", intervalKm: 40000, intervalMonths: 36, category: "Engine", color: "yellow" },
  { id: "coolant", name: "Coolant", intervalKm: 40000, intervalMonths: 36, category: "Fluids", color: "teal" },
  { id: "timing-belt", name: "Timing belt", intervalKm: 100000, intervalMonths: 60, category: "Engine", color: "pink" },
  { id: "battery", name: "Battery", intervalKm: 60000, intervalMonths: 48, category: "Electrical", color: "slate" },
];
