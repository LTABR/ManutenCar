import { usePreferences } from "./preferences";

const messages = {
  "pt-BR": {
    personalPlanner: "Seu planejador pessoal de cuidados com o carro",
    howItWorks: "Como funciona",
    eyebrow: "UM POUCO DE CUIDADO FAZ TODA A DIFERENÇA",
    heroLineOne: "Fique à frente",
    heroLineTwo: "do inesperado.",
    heroDescription:
      "Cuide do seu carro com mais tranquilidade. Adicione as peças que você acompanha e ajudaremos a lembrar do que vem pela frente.",
    heroFootnote: "Um bom plano hoje garante uma viagem melhor amanhã.",
    careOnYourTerms: "CUIDADO DO SEU JEITO",
    oneLessThing: "Uma preocupação a menos",
    toKeepTrack: "para você acompanhar",
    plannerLabel: "Planejador de manutenção do carro",
    maintenanceMadeSimple: "MANUTENÇÃO SEM COMPLICAÇÃO",
    howHeading: "Cuide do carro sem ficar na dúvida.",
    howDescription:
      "Os intervalos de revisão variam conforme o veículo e as condições de uso. Seu plano combina o intervalo de tempo e a quilometragem estimada para ajudar você a saber o que está por vir.",
    footerTagline: "Feito para os caminhos que vêm pela frente.",
    yourGarage: "SUA GARAGEM",
    garageHeading: "Vamos conhecer seu carro",
    yourCars: "Seus carros",
    addCar: "Adicionar carro",
    carModel: "Modelo do carro",
    chooseCarModel: "Escolha o modelo do carro",
    otherNotListed: "Outro / não listado",
    chooseModelWarning: "Escolha o modelo do carro para personalizar seu plano.",
    modelHint: "Assim, seu plano fica mais adequado ao seu carro.",
    averageDriving: "Sua média de uso",
    averageDistance: "Quilometragem média",
    drivingFrequency: "Frequência de uso",
    per: "por",
    week: "semana",
    month: "mês",
    year: "ano",
    distanceWarning: "Informe sua quilometragem média para incluir estimativas por distância.",
    distanceHint: "Usaremos esse valor para estimar as revisões por quilometragem.",
    maintenancePlan: "PLANO DE MANUTENÇÃO",
    part: "peça",
    parts: "peças",
    choosePart: "Escolha uma peça do carro",
    allPartsAdded: "Todas as peças foram adicionadas",
    addPartToPlan: "Adicione uma peça ao seu plano",
    add: "Adicionar",
    choosePartError: "Escolha uma peça do carro para adicionar ao plano.",
    every: "A cada",
    months: "meses",
    lastService: "ÚLTIMA REVISÃO",
    removePart: "Remover {part}",
    partsWillAppear: "Suas peças aparecerão aqui.",
    startByAdding: "Comece adicionando uma peça acima.",
    lookingAhead: "PRÓXIMAS REVISÕES",
    maintenanceOutlook: "Previsão de manutenção",
    car: "Carro",
    cars: "Carros",
    partFilterLabel: "Peça",
    inYourGarage: "na sua garagem",
    filterByCar: "Filtrar manutenção por carro",
    allCars: "Todos os carros",
    filterByPart: "Filtrar manutenção por peça",
    allParts: "Todas as peças",
    lookingGood: "Tudo em dia",
    oneItemNeedsAttention: "1 item precisa de atenção",
    manyItemsNeedAttention: "{count} itens precisam de atenção",
    item: "item",
    items: "itens",
    nothingDue: "Nenhuma revisão nos próximos 45 dias",
    dueSoonOrPast: "Próximas revisões ou revisões atrasadas",
    onTrack: "EM DIA",
    upNext: "PRÓXIMAS",
    wasDue: "Venceu em {date}",
    recommendedBy: "Recomendado até {date}",
    oneDayOverdue: "1 dia de atraso",
    manyDaysOverdue: "{count} dias de atraso",
    today: "Hoje",
    inOneDay: "Amanhã",
    inManyDays: "Em {count} dias",
    mileageEstimate: "Estimativa por quilometragem",
    timeInterval: "Intervalo de tempo",
    moreDetails: "Mais detalhes sobre {part}",
    timeLimit: "Limite de tempo",
    addAverageDistance: "Informe a quilometragem média",
    itemsPerPage: "Itens por página",
    previousPage: "Página anterior",
    previous: "Anterior",
    pageOf: "Página {page} de {pages}",
    nextPage: "Próxima página",
    next: "Próxima",
    estimateDisclaimer:
      "As estimativas são uma orientação. Siga sempre as recomendações do fabricante do veículo.",
    noMatchingMaintenance: "Nenhuma manutenção corresponde a estes filtros.",
    emptyHeading: "Sua próxima etapa no cuidado com o carro começa aqui.",
    emptyDescription:
      "Adicione uma peça e a data da última revisão. Calcularemos uma estimativa para ajudar você a se planejar.",
    choosePartStep: "Escolha uma peça",
    addLastServiceStep: "Informe a última revisão",
    seeNextStep: "Veja o que vem por aí",
    scheduleFooter: "Pequenos cuidados hoje. Mais tranquilidade na estrada.",
    theme: "Tema",
    lightMode: "Tema claro",
    darkMode: "Tema escuro",
    language: "Idioma",
    home: "Página inicial do ManutenCar",
  },
  en: {
    personalPlanner: "Your personal car care planner",
    howItWorks: "How it works",
    eyebrow: "A LITTLE CARE GOES A LONG WAY",
    heroLineOne: "Stay ahead of",
    heroLineTwo: "the unexpected.",
    heroDescription:
      "A calmer way to care for your car. Add the parts you maintain and we’ll help you keep an eye on what’s coming up.",
    heroFootnote: "A good plan today makes for a better drive tomorrow.",
    careOnYourTerms: "CARE, ON YOUR TERMS",
    oneLessThing: "One less thing",
    toKeepTrack: "to keep track of",
    plannerLabel: "Car maintenance planner",
    maintenanceMadeSimple: "MAINTENANCE, MADE SIMPLE",
    howHeading: "Take the guesswork out of car care.",
    howDescription:
      "Service intervals vary by vehicle and driving conditions. Your plan combines the time interval and your estimated mileage to help you know what might be coming up.",
    footerTagline: "Made for the miles ahead.",
    yourGarage: "YOUR GARAGE",
    garageHeading: "Let’s get to know your car",
    yourCars: "Your cars",
    addCar: "Add car",
    carModel: "Car model",
    chooseCarModel: "Choose your car model",
    otherNotListed: "Other / not listed",
    chooseModelWarning: "Choose a car model to make your plan more specific.",
    modelHint: "This helps keep your plan personal to your car.",
    averageDriving: "Your average driving",
    averageDistance: "Average distance driven",
    drivingFrequency: "Driving frequency",
    per: "per",
    week: "week",
    month: "month",
    year: "year",
    distanceWarning: "Add your average distance to include mileage-based estimates.",
    distanceHint: "We’ll use this to estimate your mileage-based service dates.",
    maintenancePlan: "MAINTENANCE PLAN",
    part: "part",
    parts: "parts",
    choosePart: "Choose a car part",
    allPartsAdded: "All parts added",
    addPartToPlan: "Add a part to your plan",
    add: "Add",
    choosePartError: "Choose a car part to add to your plan.",
    every: "Every",
    months: "months",
    lastService: "LAST SERVICE",
    removePart: "Remove {part}",
    partsWillAppear: "Your parts will show up here.",
    startByAdding: "Start by adding one above.",
    lookingAhead: "LOOKING AHEAD",
    maintenanceOutlook: "Your maintenance outlook",
    car: "Car",
    cars: "cars",
    partFilterLabel: "Part",
    inYourGarage: "in your garage",
    filterByCar: "Filter maintenance by car",
    allCars: "All cars",
    filterByPart: "Filter maintenance by part",
    allParts: "All parts",
    lookingGood: "Looking good",
    oneItemNeedsAttention: "1 item needs attention",
    manyItemsNeedAttention: "{count} items need attention",
    item: "item",
    items: "items",
    nothingDue: "Nothing due in the next 45 days",
    dueSoonOrPast: "Due soon or already past due",
    onTrack: "ON TRACK",
    upNext: "UP NEXT",
    wasDue: "Was due {date}",
    recommendedBy: "Recommended by {date}",
    oneDayOverdue: "1d overdue",
    manyDaysOverdue: "{count}d overdue",
    today: "Today",
    inOneDay: "In 1 day",
    inManyDays: "In {count} days",
    mileageEstimate: "Mileage estimate",
    timeInterval: "Time interval",
    moreDetails: "More details for {part}",
    timeLimit: "Time limit",
    addAverageDistance: "Add average distance",
    itemsPerPage: "Items per page",
    previousPage: "Previous page",
    previous: "Previous",
    pageOf: "Page {page} of {pages}",
    nextPage: "Next page",
    next: "Next",
    estimateDisclaimer:
      "Estimates are a helpful guide. Always follow your vehicle manufacturer’s recommendations.",
    noMatchingMaintenance: "No maintenance matches these filters.",
    emptyHeading: "Your next chapter in car care starts here.",
    emptyDescription:
      "Add a part and its last service date. We’ll work out a helpful estimate for what’s next.",
    choosePartStep: "Choose a part",
    addLastServiceStep: "Add last service",
    seeNextStep: "See what’s next",
    scheduleFooter: "Little check-ins now. Happier miles later.",
    theme: "Theme",
    lightMode: "Light mode",
    darkMode: "Dark mode",
    language: "Language",
    home: "ManutenCar home",
  },
} as const;

export type LocaleType = keyof typeof messages;
export type MessageKeyType = keyof (typeof messages)["en"];

export const localeMetadata: Record<
  LocaleType,
  {
    label: string;
    intl: string;
    documentTitle: string;
    documentDescription: string;
  }
> = {
  en: {
    label: "English",
    intl: "en-US",
    documentTitle: "ManutenCar — Car care, made simple",
    documentDescription:
      "A personal plan for staying ahead of your car maintenance.",
  },
  "pt-BR": {
    label: "Português (Brasil)",
    intl: "pt-BR",
    documentTitle: "ManutenCar — Cuidado com o carro sem complicação",
    documentDescription:
      "Um plano pessoal para manter a manutenção do seu carro em dia.",
  },
};

export const localeOptions = (Object.keys(messages) as LocaleType[]).map(
  (locale) => ({ value: locale, label: localeMetadata[locale].label }),
);

export function isLocaleType(value: string | null): value is LocaleType {
  return value !== null && Object.prototype.hasOwnProperty.call(messages, value);
}

const partNames: Record<string, Partial<Record<LocaleType, string>>> = {
  "engine-oil": { en: "Engine oil & filter", "pt-BR": "Óleo do motor e filtro" },
  "air-filter": { en: "Engine air filter", "pt-BR": "Filtro de ar do motor" },
  "cabin-filter": { en: "Cabin air filter", "pt-BR": "Filtro de ar da cabine" },
  "brake-fluid": { en: "Brake fluid", "pt-BR": "Fluido de freio" },
  "brake-pads": { en: "Brake pads", "pt-BR": "Pastilhas de freio" },
  "spark-plugs": { en: "Spark plugs", "pt-BR": "Velas de ignição" },
  coolant: { en: "Coolant", "pt-BR": "Líquido de arrefecimento" },
  "timing-belt": { en: "Timing belt", "pt-BR": "Correia dentada" },
  battery: { en: "Battery", "pt-BR": "Bateria" },
};

export function useTranslation() {
  const { locale } = usePreferences();
  const t = (key: MessageKeyType) => messages[locale][key];
  const partName = (id: string, fallback: string) =>
    partNames[id]?.[locale] ?? fallback;
  const formatNumber = (value: number) =>
    new Intl.NumberFormat(localeMetadata[locale].intl).format(value);
  const formatDate = (date: Date) =>
    new Intl.DateTimeFormat(localeMetadata[locale].intl, {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(date);
  const interpolate = (
    message: string,
    values: Record<string, string | number>,
  ) =>
    message.replace(/\{(\w+)\}/g, (_, key: string) =>
      String(values[key] ?? `{${key}}`),
    );

  return { locale, t, partName, formatNumber, formatDate, interpolate };
}
