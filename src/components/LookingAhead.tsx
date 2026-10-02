import { useState } from "react";
import { useAppSelector } from "../store/hooks";
import type { PartType, TrackedPartType } from "../types/maintenance";
import { Icon } from "./Icon";
import { Card, PartMarker, SectionKicker } from "./styles/sharedStyles";
import { useTranslation } from "../langsDict";

type ScheduleStatusType = "overdue" | "soon" | "on-track";

export type ScheduledItemType = TrackedPartType & {
  carId: string;
  carModel: string;
  kmPerMonth: number;
  part: PartType;
  nextDue: Date;
  calendarDue: Date;
  mileageDue: Date;
  daysUntil: number;
  status: ScheduleStatusType;
};

type LookingAheadPropTypes = {
  scheduled: ScheduledItemType[];
};

export function LookingAhead({ scheduled }: LookingAheadPropTypes) {
  const { t, partName, formatDate, formatNumber, interpolate } =
    useTranslation();
  const cars = useAppSelector((state) => state.maintenance.cars);
  const [carFilter, setCarFilter] = useState("all");
  const [partFilter, setPartFilter] = useState("all");
  const [pageSize, setPageSize] = useState(5);
  const [page, setPage] = useState(1);
  const filteredSchedule = scheduled.filter(
    (item) =>
      (carFilter === "all" || item.carId === carFilter) &&
      (partFilter === "all" || item.partId === partFilter),
  );
  const pageCount = Math.max(1, Math.ceil(filteredSchedule.length / pageSize));
  const currentPage = Math.min(page, pageCount);
  const visibleSchedule = filteredSchedule.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize,
  );
  const dueSoonCount = filteredSchedule.filter(
    (item) => item.status !== "on-track",
  ).length;
  const availableParts = [
    ...new Map(scheduled.map((item) => [item.partId, item.part])).values(),
  ].sort((a, b) => a.name.localeCompare(b.name));

  return (
    <Card as="section" className="schedule-card" aria-live="polite">
      <div className="schedule-header">
        <div>
          <SectionKicker>{t("lookingAhead")}</SectionKicker>
          <h2>{t("maintenanceOutlook")}</h2>
          <p>
            <Icon name="car" size={15} /> {formatNumber(cars.length)}{" "}
            {cars.length === 1 ? t("car").toLowerCase() : t("cars").toLowerCase()} {t("inYourGarage")}
          </p>
        </div>
        <span className="schedule-spark">
          <Icon name="spark" size={18} />
        </span>
      </div>

      <div className="schedule-filters">
        <label>
          <span>{t("car")}</span>
          <select
            aria-label={t("filterByCar")}
            value={carFilter}
            onChange={(event) => {
              setCarFilter(event.target.value);
              setPage(1);
            }}
          >
            <option value="all">{t("allCars")}</option>
            {cars.map((car, index) => (
              <option key={car.id} value={car.id}>
                {car.model
                  ? `${car.model} · ${t("car")} ${index + 1}`
                  : `${t("car")} ${index + 1}`}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>{t("partFilterLabel")}</span>
          <select
            aria-label={t("filterByPart")}
            value={partFilter}
            onChange={(event) => {
              setPartFilter(event.target.value);
              setPage(1);
            }}
          >
            <option value="all">{t("allParts")}</option>
            {availableParts.map((part) => (
              <option key={part.id} value={part.id}>
                {partName(part.id, part.name)}
              </option>
            ))}
          </select>
        </label>
      </div>

      {filteredSchedule.length > 0 ? (
        <>
          <div className="summary-strip">
            <span className="summary-icon">
              <Icon name="calendar" size={17} />
            </span>
            <span>
              <strong>
                {dueSoonCount === 0
                  ? t("lookingGood")
                  : dueSoonCount === 1
                    ? t("oneItemNeedsAttention")
                    : interpolate(t("manyItemsNeedAttention"), {
                        count: formatNumber(dueSoonCount),
                      })}
              </strong>
              <small>
                {dueSoonCount === 0
                  ? t("nothingDue")
                  : t("dueSoonOrPast")}
              </small>
            </span>
            <span
              className={`summary-badge ${dueSoonCount === 0 ? "badge-green" : "badge-amber"}`}
            >
              {dueSoonCount === 0 ? t("onTrack") : t("upNext")}
            </span>
          </div>
          <div className="schedule-list">
            {visibleSchedule.map(
              ({
                id,
                carId,
                carModel,
                kmPerMonth,
                part,
                nextDue,
                calendarDue,
                mileageDue,
                daysUntil,
                status,
              }) => (
                <article className="schedule-item" key={id}>
                  <PartMarker $tone={part.color} className="part-marker">
                    <Icon name="wrench" size={16} />
                  </PartMarker>
                  <div className="schedule-item-main">
                    <div className="schedule-item-title">
                      <strong>{partName(part.id, part.name)}</strong>
                      <span className={`status-dot ${status}`} />
                    </div>
                    <div className="schedule-item-detail">
                      <Icon name="calendar" size={13} />
                      <span>
                        {daysUntil < 0
                          ? interpolate(t("wasDue"), { date: formatDate(nextDue) })
                          : interpolate(t("recommendedBy"), {
                              date: formatDate(nextDue),
                            })}
                      </span>
                    </div>
                    <div className="schedule-car-name">
                      <Icon name="car" size={12} />
                      {carModel
                        ? `${carModel} · ${t("car")} ${cars.findIndex((car) => car.id === carId) + 1}`
                        : `${t("car")} ${cars.findIndex((car) => car.id === carId) + 1}`}
                    </div>
                  </div>
                  <div className="schedule-item-date">
                    <strong
                      className={status === "overdue" ? "overdue-text" : ""}
                    >
                      {daysUntil < 0
                        ? Math.abs(daysUntil) === 1
                          ? t("oneDayOverdue")
                          : interpolate(t("manyDaysOverdue"), {
                              count: formatNumber(Math.abs(daysUntil)),
                            })
                        : daysUntil === 0
                          ? t("today")
                          : daysUntil === 1
                            ? t("inOneDay")
                            : interpolate(t("inManyDays"), {
                                count: formatNumber(daysUntil),
                              })}
                    </strong>
                    <span>
                      {nextDue.getTime() < calendarDue.getTime()
                        ? t("mileageEstimate")
                        : t("timeInterval")}
                    </span>
                  </div>
                  <details className="schedule-details">
                    <summary
                      aria-label={interpolate(t("moreDetails"), {
                        part: partName(part.id, part.name),
                      })}
                    >
                      <span>i</span>
                    </summary>
                    <div className="details-popover">
                      {t("timeLimit")}: {formatDate(calendarDue)}
                      <br />
                      {t("mileageEstimate")}:{" "}
                      {kmPerMonth > 0
                        ? formatDate(mileageDue)
                        : t("addAverageDistance")}
                    </div>
                  </details>
                </article>
              ),
            )}
          </div>
          <nav
            className="schedule-pagination"
            aria-label={t("maintenanceOutlook")}
          >
            <label>
              <span>{t("itemsPerPage")}</span>
              <select
                aria-label={t("itemsPerPage")}
                value={pageSize}
                onChange={(event) => {
                  setPageSize(Number(event.target.value));
                  setPage(1);
                }}
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={25}>25</option>
              </select>
            </label>
            <div className="schedule-page-controls">
              <button
                type="button"
                onClick={() => setPage(currentPage - 1)}
                disabled={currentPage === 1}
                aria-label={t("previousPage")}
              >
                {t("previous")}
              </button>
              <span>{interpolate(t("pageOf"), {
                page: formatNumber(currentPage),
                pages: formatNumber(pageCount),
              })}</span>
              <button
                type="button"
                onClick={() => setPage(currentPage + 1)}
                disabled={currentPage === pageCount}
                aria-label={t("nextPage")}
              >
                {t("next")}
              </button>
            </div>
          </nav>
          <div className="estimate-note">
            <span className="note-info">i</span> {t("estimateDisclaimer")}
          </div>
        </>
      ) : scheduled.length > 0 ? (
        <div className="schedule-no-results">
          {t("noMatchingMaintenance")}
        </div>
      ) : (
        <div className="schedule-empty">
          <div className="empty-calendar">
            <Icon name="calendar" size={27} />
            <span className="calendar-plus">+</span>
          </div>
          <h3>{t("emptyHeading")}</h3>
          <p>{t("emptyDescription")}</p>
          <div className="empty-steps">
            <span>
              <i>01</i> {t("choosePartStep")}
            </span>
            <span className="step-line" />
            <span>
              <i>02</i> {t("addLastServiceStep")}
            </span>
            <span className="step-line" />
            <span>
              <i>03</i> {t("seeNextStep")}
            </span>
          </div>
        </div>
      )}
      <div className="schedule-footer">
        <span className="footer-leaf">✳</span> {t("scheduleFooter")}
      </div>
    </Card>
  );
}
