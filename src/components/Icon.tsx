import type { ReactNode } from "react";

export type IconNameType =
  | "car"
  | "calendar"
  | "plus"
  | "arrow"
  | "spark"
  | "wrench"
  | "trash"
  | "road"
  | "chevron"
  | "sun"
  | "moon";

export function Icon({
  name,
  size = 20,
}: {
  name: IconNameType;
  size?: number;
}) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true as const,
  };
  const paths: Record<IconNameType, ReactNode> = {
    car: (
      <>
        <path d="m5 11 1.5-4.5A2 2 0 0 1 8.4 5h7.2a2 2 0 0 1 1.9 1.5L19 11" />
        <path d="M3 11h18v7H3zM6 18v2m12-2v2M3 14h2m14 0h2" />
        <circle cx="7.5" cy="14.5" r=".5" fill="currentColor" />
        <circle cx="16.5" cy="14.5" r=".5" fill="currentColor" />
      </>
    ),
    calendar: (
      <>
        <rect x="3.5" y="5" width="17" height="15.5" rx="2" />
        <path d="M7.5 3v4m9-4v4M3.5 9h17" />
        <path d="m9 14 2 2 4-4" />
      </>
    ),
    plus: <path d="M12 5v14m-7-7h14" />,
    arrow: <path d="M5 12h14m-6-6 6 6-6 6" />,
    spark: (
      <>
        <path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z" />
        <path d="m19 15 .8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15Z" />
      </>
    ),
    wrench: (
      <path d="M14.7 6.3a5 5 0 0 0-6.4 6.4l-5.5 5.5a2.1 2.1 0 0 0 3 3l5.5-5.5a5 5 0 0 0 6.4-6.4l-3.1 3.1-3-3 3.1-3.1Z" />
    ),
    trash: <path d="M4 7h16m-10 4v6m4-6v6M5.5 7l1 13h11l1-13M9 7V4h6v3" />,
    road: <path d="M8 3 5 21m11-18 3 18M12 5v3m0 4v3m0 4v2" />,
    chevron: <path d="m9 18 6-6-6-6" />,
    sun: (
      <>
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" />
      </>
    ),
    moon: <path d="M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5 8.5 8.5 0 1 0 20.5 14.2Z" />,
  };
  return <svg {...common}>{paths[name]}</svg>;
}
