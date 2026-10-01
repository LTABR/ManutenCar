import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";
import type { LocaleType } from "./langsDict";

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
  return value === "pt-BR" ? "pt-BR" : "en";
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
    document.title =
      locale === "pt-BR"
        ? "ManutenCar — Cuidado com o carro sem complicação"
        : "ManutenCar — Car care, made simple";
    document
      .querySelector('meta[name="description"]')
      ?.setAttribute(
        "content",
        locale === "pt-BR"
          ? "Um plano pessoal para manter a manutenção do seu carro em dia."
          : "A personal plan for staying ahead of your car maintenance.",
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
