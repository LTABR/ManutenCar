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
  orange: ["#be7951", "#fbf1e9"],
  blue: ["#5a809f", "#eef3f8"],
  green: ["#568166", "#edf4ed"],
  red: ["#ad6460", "#f8eeee"],
  purple: ["#816c9b", "#f3eff7"],
  yellow: ["#a78a47", "#f8f4e9"],
  teal: ["#4d8984", "#eaf4f2"],
  pink: ["#a76f82", "#f8eef2"],
  slate: ["#647784", "#edf1f4"],
};

const darkPartColors: Record<PartColorType, [string, string]> = {
  orange: ["#e5ad8a", "#49352a"],
  blue: ["#a5c3df", "#293b4c"],
  green: ["#a7cfad", "#2c4032"],
  red: ["#e0a09b", "#472f30"],
  purple: ["#c4aedc", "#3b3248"],
  yellow: ["#d8c17f", "#453d28"],
  teal: ["#9bcac5", "#293e3b"],
  pink: ["#d8a6b8", "#45313a"],
  slate: ["#afc0cd", "#303b43"],
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
  color: #969e98;
  background: transparent;

  &:hover {
    color: #b55c53;
  }
`;
