import { useMemo } from "react";
import { Icon } from "../components/Icon";
import { LookingAhead } from "../components/LookingAhead";
import type { ScheduledItemType } from "../components/LookingAhead";
import { SectionKicker } from "../components/styles/sharedStyles";
import { YourGarage } from "../components/YourGarage";
import { catalog } from "../data/parts";
import { useAppSelector } from "../store/hooks";
import type { PartType } from "../types/maintenance";
import { usePreferences } from "../preferences";
import { useTranslation } from "../langsDict";
// @ts-expect-error - CSS imports are handled by the bundler; type declarations are not configured in this project.
import "./styles/App.css";

function addMonths(date: Date, months: number) {
  const result = new Date(date);
  const day = result.getDate();
  result.setDate(1);
  result.setMonth(result.getMonth() + months);
  const lastDay = new Date(
    result.getFullYear(),
    result.getMonth() + 1,
    0,
  ).getDate();
  result.setDate(Math.min(day, lastDay));
  return result;
}

function calendarDaysFromNow(date: Date) {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const due = new Date(date);
  due.setHours(0, 0, 0, 0);
  return Math.ceil((due.getTime() - now.getTime()) / 86400000);
}

function App() {
  const cars = useAppSelector((state) => state.maintenance.cars);
  const { theme, setTheme, locale, setLocale } = usePreferences();
  const { t } = useTranslation();

  const scheduled = useMemo<ScheduledItemType[]>(
    () =>
      cars.flatMap((car) => {
        const value = Number(car.distance);
        const kmPerMonth =
          !Number.isFinite(value) || value <= 0
            ? 0
            : car.frequency === "week"
              ? (value * 52) / 12
              : car.frequency === "year"
                ? value / 12
                : value;
        return car.parts.map((tracked) => {
          const part = catalog.find(
            (item: PartType) => item.id === tracked.partId,
          );
          if (!part) return null;
          const servicedAt = new Date(`${tracked.lastServiced}T12:00:00`);
          const calendarDue = addMonths(servicedAt, part.intervalMonths);
          const mileageDue = new Date(servicedAt);
          if (kmPerMonth > 0) {
            mileageDue.setDate(
              mileageDue.getDate() +
                Math.ceil((part.intervalKm / kmPerMonth) * 30.4375),
            );
          }
          const nextDue =
            kmPerMonth > 0 && mileageDue < calendarDue
              ? mileageDue
              : calendarDue;
          const daysUntil = calendarDaysFromNow(nextDue);
          const status: ScheduledItemType["status"] =
            daysUntil < 0 ? "overdue" : daysUntil <= 45 ? "soon" : "on-track";
          return {
            ...tracked,
            carId: car.id,
            carModel: car.model,
            kmPerMonth,
            part,
            nextDue,
            calendarDue,
            mileageDue,
            daysUntil,
            status,
          };
        });
      })
      .filter((item): item is ScheduledItemType => item !== null)
      .sort((a, b) => a.nextDue.getTime() - b.nextDue.getTime()),
    [cars],
  );

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label={t("home")}>
          <span className="brand-mark">
            <Icon name="wrench" size={19} />
          </span>
          <span>
            ManutenCar<span className="brand-period">.</span>
          </span>
        </a>
        <div className="topbar-note">
          <span className="live-dot" /> {t("personalPlanner")}
        </div>
        <div className="topbar-controls">
          <button
            className="preference-button"
            type="button"
            aria-label={theme === "dark" ? t("lightMode") : t("darkMode")}
            title={theme === "dark" ? t("lightMode") : t("darkMode")}
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            <Icon name={theme === "dark" ? "sun" : "moon"} size={16} />
          </button>
          <button
            className="preference-button language-button"
            type="button"
            aria-label={
              locale === "en" ? t("switchToPortuguese") : t("switchToEnglish")
            }
            onClick={() => setLocale(locale === "en" ? "pt-BR" : "en")}
          >
            {locale === "en" ? "PT-BR" : "EN"}
          </button>
          <a className="topbar-link" href="#how-it-works">
            {t("howItWorks")} <Icon name="arrow" size={15} />
          </a>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow">
              <span className="eyebrow-line" /> {t("eyebrow")}
            </div>
            <h1>
              {t("heroLineOne")}
              <br />
              <span>{t("heroLineTwo")}</span>
            </h1>
            <p>{t("heroDescription")}</p>
            <div className="hero-footnote">
              <span className="footnote-icon">
                <Icon name="spark" size={15} />
              </span>
              {t("heroFootnote")}
            </div>
          </div>
          <div className="hero-art" aria-hidden="true">
            <div className="art-circle art-circle-back" />
            <div className="art-circle art-circle-front" />
            <div className="art-label">
              <span className="art-label-dot" /> {t("careOnYourTerms")}
            </div>
            <div className="art-car">
              <Icon name="car" size={142} />
            </div>
            <div className="art-road" />
            <div className="art-card">
              <span className="art-card-icon">
                <Icon name="calendar" size={18} />
              </span>
              <span>
                <strong>{t("oneLessThing")}</strong>
                <small>{t("toKeepTrack")}</small>
              </span>
              <span className="art-check">✓</span>
            </div>
          </div>
        </section>

        <section className="planner-grid" aria-label={t("plannerLabel")}>
          <YourGarage />
          <LookingAhead scheduled={scheduled} />
        </section>

        <section className="how-section" id="how-it-works">
          <div>
            <SectionKicker>
              {t("maintenanceMadeSimple")}
            </SectionKicker>
            <h2>{t("howHeading")}</h2>
          </div>
          <p>{t("howDescription")}</p>
        </section>
      </main>
      <footer className="page-footer">
        <span>
          ManutenCar<span className="brand-period">.</span>
        </span>
        <span>{t("footerTagline")}</span>
      </footer>
    </div>
  );
}

export default App;
