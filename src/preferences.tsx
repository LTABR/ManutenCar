import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";
import {
  isLocaleType,
  localeMetadata,
  type LocaleType,
} from "./langsDict";

export type ThemeType = "light" | "dark";

type PreferencesType = {
  locale: LocaleType;
  theme: ThemeType;
  setLocale: (locale: LocaleType) => void;
  setTheme: (theme: ThemeType) => void;
};

const PreferencesContext = createContext<PreferencesType | null>(null);

function storedLocale(): LocaleType {
  const value = localStorage.getItem("manutencar-locale");
  return isLocaleType(value) ? value : "en";
}

function storedTheme(): ThemeType {
  return localStorage.getItem("manutencar-theme") === "light" ? "light" : "dark";
}

export function PreferencesProvider({ children }: PropsWithChildren) {
  const [locale, setLocale] = useState<LocaleType>(storedLocale);
  const [theme, setTheme] = useState<ThemeType>(storedTheme);

  useEffect(() => {
    localStorage.setItem("manutencar-locale", locale);
    document.documentElement.lang = locale;
    document.title = localeMetadata[locale].documentTitle;
    document
      .querySelector('meta[name="description"]')
      ?.setAttribute(
        "content",
        localeMetadata[locale].documentDescription,
      );
  }, [locale]);

  useEffect(() => {
    localStorage.setItem("manutencar-theme", theme);
    document.documentElement.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute(
      "content",
      theme === "dark" ? "#151b18" : "#f5f6f2",
    );
  }, [theme]);

  const value = useMemo(
    () => ({ locale, theme, setLocale, setTheme }),
    [locale, theme],
  );

  return (
    <PreferencesContext.Provider value={value}>
      {children}
    </PreferencesContext.Provider>
  );
}

export function usePreferences() {
  const preferences = useContext(PreferencesContext);
  if (!preferences) {
    throw new Error("usePreferences must be used within PreferencesProvider");
  }
  return preferences;
}
