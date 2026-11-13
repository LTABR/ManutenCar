import { useState } from "react";
import { catalog } from "../data/parts";
import {
  addPart,
  addCar,
  removeCar,
  removePart,
  replaceCar,
  replacePart,
  selectCar,
  setDistance,
  setFormError,
  setFrequency,
  setModel,
  setSelectedPart,
} from "../store/maintenanceSlice";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import type { FrequencyType } from "../types/maintenance";
import { garageApi } from "../api/garage";
import { useTranslation } from "../langsDict";
import { Icon } from "./Icon";
import {
  Card,
  IconButton,
  PartMarker,
  SectionKicker,
  SelectControl,
} from "./styles/sharedStyles";

const carModels = [
  "Toyota Corolla",
  "Honda Civic",
  "Volkswagen Golf",
  "Ford Focus",
  "Hyundai i30",
  "Chevrolet Onix",
  "Renault Clio",
  "Other / not listed",
];

function getTodayString() {
  const today = new Date();
  return [
    today.getFullYear(),
    String(today.getMonth() + 1).padStart(2, "0"),
    String(today.getDate()).padStart(2, "0"),
  ].join("-");
}

export function YourGarage() {
  const { t, partName, formatNumber, interpolate } = useTranslation();
  const dispatch = useAppDispatch();
  const { cars, activeCarId, selectedPart, formError } = useAppSelector(
    (state) => state.maintenance,
  );
  const activeCar = cars.find((car) => car.id === activeCarId);
  const parts = activeCar?.parts ?? [];
  const [isAddingCar, setIsAddingCar] = useState(false);
  const [isAddingPart, setIsAddingPart] = useState(false);
  const [removingCarId, setRemovingCarId] = useState<string | null>(null);
  const [removingPartId, setRemovingPartId] = useState<string | null>(null);
  const addableParts = catalog.filter(
    (part) => !parts.some((tracked) => tracked.partId === part.id),
  );

  async function handleAddCar() {
    setIsAddingCar(true);
    dispatch(setFormError(""));
    try {
      const car = await garageApi.createCar({
        model: "",
        distance: "250",
        frequency: "week",
      });
      dispatch(addCar(car));
    } catch (error) {
      dispatch(setFormError(error instanceof Error ? error.message : t("addCarFailed")));
    } finally {
      setIsAddingCar(false);
    }
  }

  async function handleRemoveCar(carId: string) {
    setRemovingCarId(carId);
    dispatch(setFormError(""));
    try {
      await garageApi.deleteCar(carId);
      dispatch(removeCar(carId));
    } catch (error) {
      dispatch(setFormError(error instanceof Error ? error.message : t("removeCarFailed")));
    } finally {
      setRemovingCarId(null);
    }
  }

  async function handleAddPart() {
    if (!selectedPart) {
      dispatch(setFormError("choosePartError"));
      return;
    }
    if (!activeCarId) return;
    setIsAddingPart(true);
    dispatch(setFormError(""));
    try {
      const savedPart = await garageApi.addPart(activeCarId, {
        partId: selectedPart,
        lastServiced: getTodayString(),
      });
      dispatch(addPart({ carId: activeCarId, part: savedPart }));
    } catch (error) {
      dispatch(setFormError(error instanceof Error ? error.message : t("addPartFailed")));
    } finally {
      setIsAddingPart(false);
    }
  }

  async function handleRemovePart(partId: string) {
    if (!activeCarId) return;
    setRemovingPartId(partId);
    dispatch(setFormError(""));
    try {
      await garageApi.deletePart(activeCarId, partId);
      dispatch(removePart({ carId: activeCarId, id: partId }));
    } catch (error) {
      dispatch(setFormError(error instanceof Error ? error.message : t("removePartFailed")));
    } finally {
      setRemovingPartId(null);
    }
  }

  async function saveDrivingUsage() {
    if (!activeCar) return;
    dispatch(setFormError(""));
    try {
      const updatedCar = await garageApi.updateCar(activeCar.id, {
        distance: activeCar.distance,
        frequency: activeCar.frequency,
      });
      dispatch(
        replaceCar({
          ...updatedCar,
          distance: activeCar.distance,
          frequency: activeCar.frequency,
        }),
      );
    } catch (error) {
      dispatch(
        setFormError(
          error instanceof Error ? error.message : t("updateCarFailed"),
        ),
      );
    }
  }

  return (
    <Card className="setup-card">
      <div className="card-heading">
        <div className="heading-icon">
          <Icon name="car" size={19} />
        </div>
        <div>
          <SectionKicker>{t("yourGarage")}</SectionKicker>
          <h2>{t("garageHeading")}</h2>
        </div>
      </div>

      <div className="garage-car-picker" aria-label={t("yourCars")}>
        {cars.map((car, index) => (
          <div
            className={`garage-car-item${car.id === activeCarId ? " active" : ""}`}
            key={car.id}
          >
            <button
              className={`garage-car-tab${car.id === activeCarId ? " active" : ""}`}
              type="button"
              onClick={() => dispatch(selectCar(car.id))}
              aria-pressed={car.id === activeCarId}
            >
              <Icon name="car" size={15} />
              <span>
                {car.model
                  ? `${car.model} · ${t("car")} ${index + 1}`
                  : `${t("car")} ${index + 1}`}
              </span>
            </button>
            <IconButton
              className="remove-car-button"
              type="button"
              onClick={() => void handleRemoveCar(car.id)}
              disabled={
                removingCarId !== null ||
                isAddingCar ||
                isAddingPart ||
                removingPartId !== null
              }
              aria-label={interpolate(t("removeCar"), {
                car: car.model || `${t("car")} ${index + 1}`,
              })}
              title={interpolate(t("removeCar"), {
                car: car.model || `${t("car")} ${index + 1}`,
              })}
            >
              <Icon name="trash" size={14} />
            </IconButton>
          </div>
        ))}
        <button
          className="garage-add-car"
          type="button"
          onClick={() => void handleAddCar()}
          disabled={
            isAddingCar ||
            removingCarId !== null ||
            isAddingPart ||
            removingPartId !== null
          }
        >
          <Icon name="plus" size={15} />
          <span>{isAddingCar ? t("addingCar") : t("addCar")}</span>
        </button>
      </div>

      <div className="field-group">
        <label htmlFor="car-model">{t("carModel")}</label>
        <div className="select-wrap">
          <SelectControl
            id="car-model"
            value={activeCar?.model ?? ""}
            onChange={(event) => dispatch(setModel(event.target.value))}
            disabled={!activeCar || removingCarId === activeCarId}
            onBlur={() => {
              void garageApi
                .updateCar(activeCarId, { model: activeCar?.model ?? "" })
                .catch(() => undefined);
            }}
          >
            <option value="" hidden>{t("chooseCarModel")}</option>
            {carModels.map((car) => (
              <option key={car} value={car}>
                {car === "Other / not listed" ? t("otherNotListed") : car}
              </option>
            ))}
          </SelectControl>
          <span className="select-chevron">
            <Icon name="chevron" size={16} />
          </span>
        </div>
        {activeCar && !activeCar.model.trim() && (
          <p className="field-warning" role="status">
            {t("chooseModelWarning")}
          </p>
        )}
        <span className="field-hint">
          {t("modelHint")}
        </span>
      </div>

      <div className="field-group usage-group">
        <label htmlFor="average-distance">{t("averageDriving")}</label>
        <div className="usage-input-row">
          <div className="input-with-icon">
            <Icon name="road" size={17} />
            <input
              id="average-distance"
              type="number"
              min="1"
              inputMode="numeric"
              value={activeCar?.distance ?? ""}
              disabled={!activeCar || removingCarId === activeCarId}
              onChange={(event) => dispatch(setDistance(event.target.value))}
              onBlur={() => void saveDrivingUsage()}
              aria-label={t("averageDistance")}
            />
            <span>km</span>
          </div>
          <span className="per-label">{t("per")}</span>
          <div className="select-wrap frequency-select">
            <SelectControl
              aria-label={t("drivingFrequency")}
              value={activeCar?.frequency ?? "week"}
              disabled={!activeCar || removingCarId === activeCarId}
              onChange={(event) =>
                dispatch(setFrequency(event.target.value as FrequencyType))
              }
              onBlur={() => void saveDrivingUsage()}
            >
              <option value="week">{t("week")}</option>
              <option value="month">{t("month")}</option>
              <option value="year">{t("year")}</option>
            </SelectControl>
            <span className="select-chevron">
              <Icon name="chevron" size={16} />
            </span>
          </div>
        </div>
        {activeCar && !activeCar.distance.trim() && (
          <p className="field-warning" role="status">
            {t("distanceWarning")}
          </p>
        )}
        <span className="field-hint">
          {t("distanceHint")}
        </span>
      </div>

      <div className="parts-divider">
        <span>{t("maintenancePlan")}</span>
        <span className="parts-count">
          {formatNumber(parts.length)}{" "}
          {parts.length === 1 ? t("part") : t("parts")}
        </span>
      </div>
      <div className="part-add-row">
        <div className="select-wrap">
          <SelectControl
            aria-label={t("choosePart")}
            value={selectedPart}
            onChange={(event) => dispatch(setSelectedPart(event.target.value))}
            disabled={
              !activeCar ||
              removingCarId === activeCarId ||
              addableParts.length === 0 ||
              isAddingPart
            }
          >
            <option value="" hidden>
              {addableParts.length === 0
                ? t("allPartsAdded")
                : t("addPartToPlan")}
            </option>
            {addableParts.map((part) => (
              <option key={part.id} value={part.id}>
                {partName(part.id, part.name)}
              </option>
            ))}
          </SelectControl>
          <span className="select-chevron">
            <Icon name="chevron" size={16} />
          </span>
        </div>
        <button
          className="add-button"
          type="button"
          onClick={() => void handleAddPart()}
          disabled={
            !activeCar ||
            removingCarId === activeCarId ||
            addableParts.length === 0 ||
            isAddingPart
          }
        >
          <Icon name="plus" size={18} />
          <span>{isAddingPart ? t("addingPart") : t("add")}</span>
        </button>
      </div>
      {formError && (
        <p className="form-error" role="alert">
          {formError === "choosePartError" ? t("choosePartError") : formError}
        </p>
      )}

      {parts.length > 0 ? (
        <div className="tracked-parts">
          {parts.map((tracked) => {
            const part = catalog.find((item) => item.id === tracked.partId);
            if (!part) return null;
            return (
              <div className="tracked-part" key={tracked.id}>
                <PartMarker $tone={part.color} className="part-marker">
                  <Icon name="wrench" size={16} />
                </PartMarker>
                <div className="tracked-part-info">
                  <strong>{partName(part.id, part.name)}</strong>
                  <span>
                    {t("every")} {formatNumber(part.intervalKm)} km
                    <span className="dot-separator">·</span>
                    {formatNumber(part.intervalMonths)} {t("months")}
                  </span>
                </div>
                <label
                  className="last-service-label"
                  htmlFor={`service-${tracked.id}`}
                >
                  {t("lastService")}
                </label>
                <input
                  id={`service-${tracked.id}`}
                  className="date-input"
                  type="date"
                  max={getTodayString()}
                  value={tracked.lastServiced}
                  onChange={(event) => {
                    if (event.target.value) {
                      void garageApi
                        .updatePart(activeCarId, tracked.id, {
                          lastServiced: event.target.value,
                        })
                        .then((updatedPart) =>
                          dispatch(
                            replacePart({
                              carId: activeCarId,
                              part: updatedPart,
                            }),
                          ),
                        )
                        .catch((error: unknown) =>
                          dispatch(
                            setFormError(
                              error instanceof Error
                                ? error.message
                                : t("updatePartFailed"),
                            ),
                          ),
                        );
                    }
                  }}
                />
                <IconButton
                  className="remove-button"
                  type="button"
                  onClick={() => void handleRemovePart(tracked.id)}
                  disabled={removingPartId !== null || removingCarId === activeCarId}
                  aria-label={interpolate(t("removePart"), {
                    part: partName(part.id, part.name),
                  })}
                >
                  <Icon name="trash" size={17} />
                </IconButton>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="empty-parts">
          <span className="empty-icon">
            <Icon name="wrench" size={17} />
          </span>
          <span>
            {t("partsWillAppear")}
            <br />
            <strong>{t("startByAdding")}</strong>
          </span>
        </div>
      )}
    </Card>
  );
}
