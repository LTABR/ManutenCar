import { useEffect, useMemo, useState } from "react";
import { catalog } from "../data/parts";
import { useTranslation } from "../langsDict";
import type { ScheduledItemType } from "./LookingAhead";
import {
  fetchMaintenanceDeadlinesChart,
  fetchMaintenanceHistory,
  type MaintenanceHistoryResponse,
} from "../services/maintenanceApi";
import { Icon } from "./Icon";
import { Card, SectionKicker } from "./styles/sharedStyles";

const pageSize = 10;
const statusOptions = ["completed", "scheduled", "overdue", "soon", "on-track"] as const;

type VehicleMaintenanceDetailsProps = {
  vehicleId: string;
  vehicleName: string;
  scheduled: ScheduledItemType[];
};

function statusTone(status: string | null) {
  switch (status?.toLowerCase()) {
    case "completed":
    case "on-track":
      return "maintenance-status-success";
    case "soon":
    case "scheduled":
    case "in-progress":
      return "maintenance-status-warning";
    case "overdue":
    case "cancelled":
      return "maintenance-status-danger";
    default:
      return "maintenance-status-neutral";
  }
}

export function VehicleMaintenanceDetails({
  vehicleId,
  vehicleName,
  scheduled,
}: VehicleMaintenanceDetailsProps) {
  const { t, formatDate, formatNumber, interpolate } = useTranslation();
  const statusLabels: Record<string, string> = {
    completed: t("completed"),
    scheduled: t("scheduled"),
    overdue: t("overdue"),
    soon: t("soon"),
    "on-track": t("on-track"),
  };
  const [chartUrl, setChartUrl] = useState("");
  const [chartLoading, setChartLoading] = useState(false);
  const [chartError, setChartError] = useState("");
  const [chartAttempt, setChartAttempt] = useState(0);

  const [keyword, setKeyword] = useState("");
  const [debouncedKeyword, setDebouncedKeyword] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const [history, setHistory] = useState<MaintenanceHistoryResponse | null>(null);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState("");
  const [historyAttempt, setHistoryAttempt] = useState(0);
  const categories = useMemo(
    () => [...new Set(catalog.map((part) => part.category))].sort(),
    [],
  );
  const chartDeadlines = useMemo(
    () =>
      scheduled.map((item) => ({
        label: item.part.name,
        days_until: item.daysUntil,
      })),
    [scheduled],
  );

  useEffect(() => {
    const timer = window.setTimeout(
      () => setDebouncedKeyword(keyword.trim()),
      300,
    );
    return () => window.clearTimeout(timer);
  }, [keyword]);

  useEffect(() => {
    const controller = new AbortController();
    let objectUrl = "";

    if (chartDeadlines.length === 0) {
      setChartUrl("");
      setChartError("");
      setChartLoading(false);
      return () => controller.abort();
    }

    setChartLoading(true);
    setChartError("");
    void fetchMaintenanceDeadlinesChart(
      vehicleId,
      chartDeadlines,
      controller.signal,
    )
      .then((blob) => {
        objectUrl = URL.createObjectURL(blob);
        setChartUrl(objectUrl);
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setChartError(error instanceof Error ? error.message : "Request failed");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setChartLoading(false);
      });

    return () => {
      controller.abort();
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [chartAttempt, chartDeadlines, vehicleId]);

  useEffect(() => {
    const controller = new AbortController();
    setHistoryLoading(true);
    setHistoryError("");
    void fetchMaintenanceHistory(
      vehicleId,
      {
        keyword: debouncedKeyword,
        start_date: startDate,
        end_date: endDate,
        category,
        status,
        limit: pageSize,
        offset: (page - 1) * pageSize,
      },
      controller.signal,
    )
      .then(setHistory)
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setHistory(null);
          setHistoryError(error instanceof Error ? error.message : "Request failed");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setHistoryLoading(false);
      });
    return () => controller.abort();
  }, [
    category,
    debouncedKeyword,
    endDate,
    historyAttempt,
    page,
    startDate,
    status,
    vehicleId,
  ]);

  const pageCount = Math.max(
    1,
    Math.ceil((history?.total ?? 0) / pageSize),
  );

  return (
    <section className="vehicle-maintenance" aria-label={t("vehicleMaintenance")}>
      <Card className="maintenance-chart-card">
        <div className="maintenance-section-heading">
          <div className="maintenance-heading-icon">
            <Icon name="calendar" size={18} />
          </div>
          <div>
            <SectionKicker>{t("maintenanceDeadlines")}</SectionKicker>
            <h2>{vehicleName}</h2>
          </div>
        </div>
        {chartLoading ? (
          <div className="maintenance-chart-skeleton" aria-label={t("loading")}>
            <span />
            <span />
            <span />
          </div>
        ) : chartError ? (
          <div className="maintenance-feedback maintenance-error" role="alert">
            <p>{t("maintenanceLoadError")}: {chartError}</p>
            <button
              type="button"
              onClick={() => setChartAttempt((attempt) => attempt + 1)}
            >
              {t("retry")}
            </button>
          </div>
        ) : chartDeadlines.length === 0 ? (
          <div className="maintenance-feedback">
            <p>{t("noScheduledMaintenance")}</p>
          </div>
        ) : chartUrl ? (
          <div className="maintenance-chart-image-wrap">
            <img
              className="maintenance-chart-image"
              src={chartUrl}
              alt={interpolate(t("maintenanceChartAlt"), { vehicle: vehicleName })}
            />
          </div>
        ) : null}
      </Card>

      <Card as="section" className="maintenance-history-card">
        <div className="maintenance-history-heading">
          <div>
            <SectionKicker>{t("maintenanceHistory")}</SectionKicker>
            <h2>{t("serviceRecords")}</h2>
          </div>
          {history && (
            <span className="maintenance-total">
              {formatNumber(history.total)} {t("records")}
            </span>
          )}
        </div>

        <div className="maintenance-filters">
          <label className="maintenance-search">
            <span>{t("searchMaintenance")}</span>
            <div className="maintenance-search-input">
              <Icon name="search" size={15} />
              <input
                type="search"
                value={keyword}
                onChange={(event) => {
                  setKeyword(event.target.value);
                  setPage(1);
                }}
                placeholder={t("searchMaintenancePlaceholder")}
              />
            </div>
          </label>
          <label>
            <span>{t("fromDate")}</span>
            <input
              type="date"
              value={startDate}
              max={endDate || undefined}
              onChange={(event) => {
                setStartDate(event.target.value);
                setPage(1);
              }}
            />
          </label>
          <label>
            <span>{t("toDate")}</span>
            <input
              type="date"
              value={endDate}
              min={startDate || undefined}
              onChange={(event) => {
                setEndDate(event.target.value);
                setPage(1);
              }}
            />
          </label>
          <label>
            <span>{t("category")}</span>
            <select
              value={category}
              onChange={(event) => {
                setCategory(event.target.value);
                setPage(1);
              }}
            >
              <option value="">{t("allCategories")}</option>
              {categories.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </label>
          <label>
            <span>{t("status")}</span>
            <select
              value={status}
              onChange={(event) => {
                setStatus(event.target.value);
                setPage(1);
              }}
            >
              <option value="">{t("allStatuses")}</option>
              {statusOptions.map((option) => (
                <option key={option} value={option}>
                  {t(option)}
                </option>
              ))}
            </select>
          </label>
        </div>

        {historyLoading ? (
          <div className="maintenance-history-skeleton" aria-label={t("loading")}>
            <span />
            <span />
            <span />
          </div>
        ) : historyError ? (
          <div className="maintenance-feedback maintenance-error" role="alert">
            <p>{t("maintenanceLoadError")}: {historyError}</p>
            <button
              type="button"
              onClick={() => setHistoryAttempt((attempt) => attempt + 1)}
            >
              {t("retry")}
            </button>
          </div>
        ) : history?.items.length ? (
          <>
            <div className="maintenance-record-list">
              {history.items.map((record) => (
                <article className="maintenance-record" key={record.id}>
                  <div className="maintenance-record-date">
                    <Icon name="calendar" size={15} />
                    <time dateTime={record.service_date}>
                      {formatDate(new Date(`${record.service_date}T12:00:00`))}
                    </time>
                  </div>
                  <div className="maintenance-record-content">
                    <div className="maintenance-record-title">
                      <h3>{record.title}</h3>
                      <span className={`maintenance-status ${statusTone(record.status)}`}>
                        {record.status
                          ? statusLabels[record.status.toLowerCase()] ?? record.status
                          : t("statusNotRecorded")}
                      </span>
                    </div>
                    {record.part_name && record.part_name !== record.title && (
                      <p className="maintenance-record-part">{record.part_name}</p>
                    )}
                    {record.description && (
                      <p className="maintenance-record-notes">{record.description}</p>
                    )}
                    <div className="maintenance-record-meta">
                      <span>
                        <strong>{t("mileage")}:</strong> {t("mileageNotRecorded")}
                      </span>
                      {record.category && (
                        <span><strong>{t("category")}:</strong> {record.category}</span>
                      )}
                    </div>
                  </div>
                </article>
              ))}
            </div>
            <nav className="maintenance-history-pagination" aria-label={t("maintenanceHistory")}>
              <button
                type="button"
                onClick={() => setPage((current) => current - 1)}
                disabled={page <= 1}
              >
                {t("previous")}
              </button>
              <span>{interpolate(t("pageOf"), {
                page: formatNumber(page),
                pages: formatNumber(pageCount),
              })}</span>
              <button
                type="button"
                onClick={() => setPage((current) => current + 1)}
                disabled={page >= pageCount}
              >
                {t("next")}
              </button>
            </nav>
          </>
        ) : (
          <div className="maintenance-feedback">
            <p>{debouncedKeyword || startDate || endDate || category || status
              ? t("noMatchingMaintenance")
              : t("noMaintenanceHistory")}</p>
          </div>
        )}
      </Card>
    </section>
  );
}
