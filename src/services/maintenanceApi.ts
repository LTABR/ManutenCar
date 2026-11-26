export interface MaintenanceHistoryItem {
  id: string;
  vehicle_id: string;
  part_id: string | null;
  part_name: string | null;
  service_date: string;
  title: string;
  description: string | null;
  category: string | null;
  status: string | null;
}

export interface MaintenanceHistoryResponse {
  items: MaintenanceHistoryItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface MaintenanceHistoryQuery {
  keyword?: string;
  start_date?: string;
  end_date?: string;
  category?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

export interface MaintenanceDeadline {
  label: string;
  days_until: number;
}

export interface MaintenanceDeadlineRow {
  part_id: string;
  last_serviced: string | null;
  due_date: string | null;
  days_until: number | null;
  status: "untracked" | "on-track" | "soon" | "overdue";
}

async function request(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const token = localStorage.getItem("manutencar-access-token");
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`/api${path}`, {
    ...init,
    headers,
  });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body: unknown = await response.json();
      if (
        typeof body === "object" &&
        body !== null &&
        "detail" in body &&
        typeof body.detail === "string"
      ) {
        message = body.detail;
      }
    } catch {
      // Keep the HTTP status message when the server does not return JSON.
    }
    throw new Error(message);
  }
  return response;
}

export async function fetchMaintenanceHistory(
  vehicleId: string,
  query: MaintenanceHistoryQuery,
  signal?: AbortSignal,
): Promise<MaintenanceHistoryResponse> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && value !== "") params.set(key, String(value));
  }
  const suffix = params.size > 0 ? `?${params.toString()}` : "";
  const response = await request(
    `/cars/${encodeURIComponent(vehicleId)}/maintenance-history${suffix}`,
    { signal },
  );
  return (await response.json()) as MaintenanceHistoryResponse;
}

export async function fetchMaintenanceDeadlinesChart(
  vehicleId: string,
  signal?: AbortSignal,
): Promise<Blob> {
  const response = await request(
    `/cars/${encodeURIComponent(vehicleId)}/maintenance-deadlines-chart`,
    { signal },
  );
  return response.blob();
}

export async function fetchMaintenanceDeadlines(
  vehicleId: string,
  signal?: AbortSignal,
): Promise<MaintenanceDeadlineRow[]> {
  const response = await request(
    `/cars/${encodeURIComponent(vehicleId)}/maintenance-deadlines`,
    { signal },
  );
  return (await response.json()) as MaintenanceDeadlineRow[];
}
