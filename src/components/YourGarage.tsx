import { catalog } from "../data/parts";
import {
  addPart,
  addCar,
  removePart,
  selectCar,
  setDistance,
  setFormError,
  setFrequency,
  setModel,
  setSelectedPart,
  updatePartDate,
} from "../store/maintenanceSlice";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import type { CarType, FrequencyType } from "../types/maintenance";
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
  const addableParts = catalog.filter(
    (part) => !parts.some((tracked) => tracked.partId === part.id),
  );

  async function handleAddCar() {
    try {
      const car = await garageApi.createCar({
        model: "",
        distance: "250",
        frequency: "week",
        parts: [],
      } as Omit<CarType, "id">);
      dispatch(addCar(car));
    } catch {
      // Keep the planner usable while the backend is being configured.
      dispatch(
        addCar({
          id: `car-${Date.now()}-${cars.length}`,
          model: "",
          distance: "250",
          frequency: "week",
          parts: [],
        }),
      );
    }
  }

  async function handleAddPart() {
    if (!selectedPart) {
      dispatch(setFormError("choosePartError"));
      return;
    }
    const localPart = {
      id: `${activeCarId}-${selectedPart}-${Date.now()}`,
      partId: selectedPart,
      lastServiced: getTodayString(),
    };
    try {
      const savedPart = await garageApi.addPart(activeCarId, localPart);
      dispatch(addPart({ carId: activeCarId, part: savedPart }));
    } catch {
      dispatch(addPart({ carId: activeCarId, part: localPart }));
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
          <button
            className={`garage-car-tab${car.id === activeCarId ? " active" : ""}`}
            key={car.id}
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
        ))}
        <button className="garage-add-car" type="button" onClick={handleAddCar}>
          <Icon name="plus" size={15} />
          <span>{t("addCar")}</span>
        </button>
      </div>

      <div className="field-group">
        <label htmlFor="car-model">{t("carModel")}</label>
        <div className="select-wrap">
          <SelectControl
            id="car-model"
            value={activeCar?.model ?? ""}
            onChange={(event) => dispatch(setModel(event.target.value))}
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
              onChange={(event) => dispatch(setDistance(event.target.value))}
              onBlur={() => {
                void garageApi
                  .updateCar(activeCarId, {
                    distance: activeCar?.distance ?? "",
                    frequency: activeCar?.frequency ?? "week",
                  })
                  .catch(() => undefined);
              }}
              aria-label={t("averageDistance")}
            />
            <span>km</span>
          </div>
          <span className="per-label">{t("per")}</span>
          <div className="select-wrap frequency-select">
            <SelectControl
              aria-label={t("drivingFrequency")}
              value={activeCar?.frequency ?? "week"}
              onChange={(event) =>
                dispatch(setFrequency(event.target.value as FrequencyType))
              }
              onBlur={() => {
                void garageApi
                  .updateCar(activeCarId, {
                    distance: activeCar?.distance ?? "",
                    frequency: activeCar?.frequency ?? "week",
                  })
                  .catch(() => undefined);
              }}
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
            disabled={addableParts.length === 0}
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
          onClick={handleAddPart}
          disabled={addableParts.length === 0}
        >
          <Icon name="plus" size={18} />
          <span>{t("add")}</span>
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
                      const lastServiced = event.target.value;
                      dispatch(
                        updatePartDate({
                          carId: activeCarId,
                          id: tracked.id,
                          lastServiced,
                        }),
                      );
                      void garageApi
                        .updatePart(activeCarId, tracked.id, { lastServiced })
                        .catch(() => undefined);
                    }
                  }}
                />
                <IconButton
                  className="remove-button"
                  type="button"
                  onClick={() => {
                    void garageApi
                      .deletePart(activeCarId, tracked.id)
                      .catch(() => undefined);
                    dispatch(removePart({ carId: activeCarId, id: tracked.id }));
                  }}
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
