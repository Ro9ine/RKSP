import type { ApiError, Task, TaskComment, Team, TokenResponse, User } from "../types";

/** Пустая строка = запросы на тот же origin (nginx проксирует на API в Docker/Railway). */
const API_URL = import.meta.env.VITE_API_URL ?? "";

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

export function setToken(token: string): void {
  localStorage.setItem("access_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("access_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail: ApiError = {
      status_code: response.status,
      message: response.statusText,
    };
    try {
      const body = await response.json();
      if (body.detail && typeof body.detail === "object") {
        detail = body.detail as ApiError;
      } else if (body.message) {
        detail = body as ApiError;
      }
    } catch {
      /* ignore */
    }
    throw detail;
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) =>
    request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  getMe: () => request<User>("/users/me"),

  getTeam: () => request<Team>("/team"),

  createEmployee: (data: { email: string; password: string; full_name: string }) =>
    request<User>("/users/employees", { method: "POST", body: JSON.stringify(data) }),

  getTasks: () => request<Task[]>("/tasks"),

  getMyTasks: () => request<Task[]>("/tasks/my"),

  createTask: (data: {
    title: string;
    description: string;
    assignee_id: string;
    duration_minutes: number;
  }) => request<Task>("/tasks", { method: "POST", body: JSON.stringify(data) }),

  updateTaskStatus: (taskId: string, status: "IN_PROGRESS") =>
    request<Task>(`/tasks/${taskId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),

  addComment: (taskId: string, text: string) =>
    request<TaskComment>(`/tasks/${taskId}/comments`, {
      method: "POST",
      body: JSON.stringify({ text }),
    }),

  completeTask: (taskId: string, outcome: "SUCCESS" | "FAILURE", comment: string) =>
    request<Task>(`/tasks/${taskId}/complete`, {
      method: "POST",
      body: JSON.stringify({ outcome, comment }),
    }),
};

export function durationToMinutes(value: number, unit: "hours" | "days"): number {
  return unit === "hours" ? value * 60 : value * 24 * 60;
}

export function formatDuration(minutes: number): string {
  if (minutes < 1440) {
    const hours = Math.round(minutes / 60);
    return `${hours} ч`;
  }
  const days = Math.round(minutes / 1440);
  return `${days} д`;
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("ru-RU");
}
