import styled, { css } from "styled-components";
import type { PartColorType } from "../../types/maintenance";

export const Card = styled.div`
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--surface);
`;

export const SectionKicker = styled.span`
  display: flex;
  align-items: center;
  gap: 9px;
  color: var(--muted);
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 1.25px;
`;

export const SelectControl = styled.select`
  width: 100%;
  min-width: 0;
  max-width: 100%;
  height: 39px;
  padding: 0 35px 0 12px;
  appearance: none;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 5px;
  outline: none;
  color: var(--field-text);
  background: var(--field-bg);
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: border-color 0.15s ease;

  &:focus {
    border-color: var(--focus-border);
    box-shadow: 0 0 0 3px var(--focus-ring);
  }

  &:disabled {
    cursor: not-allowed;
    color: var(--muted);
    background: var(--field-disabled);
  }
`;

const partColors: Record<PartColorType, [string, string]> = {
  orange: ["#F36808", "#FFF1E7"],
  blue: ["#14325C", "#E7EDF5"],
  navy: ["#14325C", "#E7EDF5"],
  red: ["#F36808", "#FFF1E7"],
  purple: ["#1E467A", "#E7EDF5"],
  yellow: ["#F36808", "#FFF1E7"],
  teal: ["#14325C", "#E7EDF5"],
  pink: ["#F36808", "#FFF1E7"],
  slate: ["#475569", "#E2E8F0"],
};

const darkPartColors: Record<PartColorType, [string, string]> = {
  orange: ["#FF9B55", "#4A2A12"],
  blue: ["#93B4DE", "#0E2444"],
  navy: ["#93B4DE", "#0E2444"],
  red: ["#FF9B55", "#4A2A12"],
  purple: ["#93B4DE", "#1E467A"],
  yellow: ["#FF9B55", "#4A2A12"],
  teal: ["#93B4DE", "#1E467A"],
  pink: ["#FF9B55", "#4A2A12"],
  slate: ["#CBD5E1", "#1E467A"],
};

export const PartMarker = styled.span<{ $tone: PartColorType }>`
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 7px;

  ${({ $tone }) => {
    const [foreground, background] = partColors[$tone];
    const [darkForeground, darkBackground] = darkPartColors[$tone];
    return css`
      color: ${foreground};
      background: ${background};

      :root[data-theme="dark"] & {
        color: ${darkForeground};
        background: ${darkBackground};
      }
    `;
  }}

  @media (max-width: 420px) {
    width: 28px;
    height: 28px;
  }
`;

export const IconButton = styled.button`
  display: grid;
  place-items: center;
  border: 0;
  color: #475569;
  background: transparent;

  &:hover {
    color: #F36808;
  }
`;
