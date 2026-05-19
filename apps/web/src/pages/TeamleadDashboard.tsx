import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { api, durationToMinutes, formatDate, formatDuration } from "../api/client";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../auth/AuthContext";
import type { ApiError } from "../types";

export default function TeamleadDashboard() {
  const { user, logout } = useAuth();
  const queryClient = useQueryClient();

  const teamQuery = useQuery({ queryKey: ["team"], queryFn: api.getTeam });
  const tasksQuery = useQuery({ queryKey: ["tasks"], queryFn: api.getTasks });

  const [employeeForm, setEmployeeForm] = useState({
    email: "",
    password: "password123",
    full_name: "",
  });
  const [taskForm, setTaskForm] = useState({
    title: "",
    description: "",
    assignee_id: "",
    duration_value: 4,
    duration_unit: "hours" as "hours" | "days",
  });
  const [error, setError] = useState("");

  const createEmployee = useMutation({
    mutationFn: api.createEmployee,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["team"] });
      setEmployeeForm({ email: "", password: "password123", full_name: "" });
    },
    onError: (err: ApiError) => setError(err.message),
  });

  const createTask = useMutation({
    mutationFn: api.createTask,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["tasks"] });
      setTaskForm({
        title: "",
        description: "",
        assignee_id: "",
        duration_value: 4,
        duration_unit: "hours",
      });
    },
    onError: (err: ApiError) => setError(err.message),
  });

  const handleEmployeeSubmit = (event: FormEvent) => {
    event.preventDefault();
    setError("");
    createEmployee.mutate(employeeForm);
  };

  const handleTaskSubmit = (event: FormEvent) => {
    event.preventDefault();
    setError("");
    const duration_minutes = durationToMinutes(taskForm.duration_value, taskForm.duration_unit);
    createTask.mutate({
      title: taskForm.title,
      description: taskForm.description,
      assignee_id: taskForm.assignee_id,
      duration_minutes,
    });
  };

  const members = teamQuery.data?.members ?? [];
  const tasks = tasksQuery.data ?? [];

  return (
    <div className="app-layout">
      <header className="header">
        <div>
          <h1>Панель тимлида</h1>
          <p style={{ color: "#64748b" }}>{user?.full_name}</p>
        </div>
        <button className="btn btn-secondary" onClick={logout}>
          Выйти
        </button>
      </header>

      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>Команда: {teamQuery.data?.name ?? "..."}</h2>
        <ul style={{ margin: "1rem 0", paddingLeft: "1.25rem" }}>
          {members.map((m) => (
            <li key={m.id}>
              {m.user?.full_name} — {m.user?.email}
            </li>
          ))}
        </ul>
        <h3>Добавить сотрудника</h3>
        <form onSubmit={handleEmployeeSubmit}>
          <div className="form-group">
            <label>ФИО</label>
            <input
              value={employeeForm.full_name}
              onChange={(e) => setEmployeeForm({ ...employeeForm, full_name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={employeeForm.email}
              onChange={(e) => setEmployeeForm({ ...employeeForm, email: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Пароль</label>
            <input
              type="password"
              value={employeeForm.password}
              onChange={(e) => setEmployeeForm({ ...employeeForm, password: e.target.value })}
              required
              minLength={6}
            />
          </div>
          <button className="btn" type="submit" disabled={createEmployee.isPending}>
            Добавить
          </button>
        </form>
      </section>

      <section className="card">
        <h2>Новая задача</h2>
        <form onSubmit={handleTaskSubmit}>
          <div className="form-group">
            <label>Название</label>
            <input
              value={taskForm.title}
              onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Описание</label>
            <textarea
              value={taskForm.description}
              onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
              rows={3}
            />
          </div>
          <div className="form-group">
            <label>Исполнитель</label>
            <select
              value={taskForm.assignee_id}
              onChange={(e) => setTaskForm({ ...taskForm, assignee_id: e.target.value })}
              required
            >
              <option value="">Выберите сотрудника</option>
              {members.map((m) => (
                <option key={m.user_id} value={m.user_id}>
                  {m.user?.full_name}
                </option>
              ))}
            </select>
          </div>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label>Срок</label>
              <input
                type="number"
                min={1}
                max={taskForm.duration_unit === "hours" ? 336 : 14}
                value={taskForm.duration_value}
                onChange={(e) =>
                  setTaskForm({ ...taskForm, duration_value: Number(e.target.value) })
                }
                required
              />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label>Единица</label>
              <select
                value={taskForm.duration_unit}
                onChange={(e) =>
                  setTaskForm({
                    ...taskForm,
                    duration_unit: e.target.value as "hours" | "days",
                  })
                }
              >
                <option value="hours">Часы</option>
                <option value="days">Дни</option>
              </select>
            </div>
          </div>
          <button className="btn" type="submit" disabled={createTask.isPending}>
            Назначить задачу
          </button>
        </form>
      </section>

      <section>
        <h2 style={{ marginBottom: "1rem" }}>Задачи команды</h2>
        <div className="task-grid">
          {tasks.map((task) => (
            <article key={task.id} className="card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                <h3>{task.title}</h3>
                <StatusBadge status={task.status} />
              </div>
              <p style={{ margin: "0.5rem 0", color: "#64748b" }}>{task.description}</p>
              <p>
                <strong>Исполнитель:</strong> {task.assignee?.full_name}
              </p>
              <p>
                <strong>Срок:</strong> {formatDuration(task.duration_minutes)} (до{" "}
                {formatDate(task.due_at)})
              </p>
              {task.completion && (
                <p style={{ marginTop: "0.5rem" }}>
                  <strong>Результат:</strong> {task.completion.outcome === "SUCCESS" ? "Успех" : "Неудача"} —{" "}
                  {task.completion.comment}
                </p>
              )}
              {task.comments.length > 0 && (
                <div style={{ marginTop: "0.75rem" }}>
                  <strong>Комментарии:</strong>
                  <ul style={{ paddingLeft: "1rem", marginTop: "0.25rem" }}>
                    {task.comments.map((c) => (
                      <li key={c.id}>
                        {c.author?.full_name}: {c.text}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
