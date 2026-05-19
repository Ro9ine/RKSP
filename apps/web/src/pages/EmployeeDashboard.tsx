import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { api, formatDate, formatDuration } from "../api/client";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../auth/AuthContext";
import type { ApiError, Task } from "../types";

function TaskCard({ task }: { task: Task }) {
  const queryClient = useQueryClient();
  const [comment, setComment] = useState("");
  const [completeComment, setCompleteComment] = useState("");
  const [error, setError] = useState("");

  const isActive = task.status === "ASSIGNED" || task.status === "IN_PROGRESS";

  const startTask = useMutation({
    mutationFn: () => api.updateTaskStatus(task.id, "IN_PROGRESS"),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["myTasks"] }),
    onError: (err: ApiError) => setError(err.message),
  });

  const addComment = useMutation({
    mutationFn: (text: string) => api.addComment(task.id, text),
    onSuccess: () => {
      setComment("");
      void queryClient.invalidateQueries({ queryKey: ["myTasks"] });
    },
    onError: (err: ApiError) => setError(err.message),
  });

  const completeTask = useMutation({
    mutationFn: ({ outcome, text }: { outcome: "SUCCESS" | "FAILURE"; text: string }) =>
      api.completeTask(task.id, outcome, text),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["myTasks"] }),
    onError: (err: ApiError) => setError(err.message),
  });

  const handleComment = (event: FormEvent) => {
    event.preventDefault();
    setError("");
    if (!comment.trim()) return;
    addComment.mutate(comment.trim());
  };

  const handleComplete = (outcome: "SUCCESS" | "FAILURE") => {
    setError("");
    if (!completeComment.trim()) {
      setError("Комментарий обязателен при завершении задачи");
      return;
    }
    completeTask.mutate({ outcome, text: completeComment.trim() });
  };

  return (
    <article className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
        <h3>{task.title}</h3>
        <StatusBadge status={task.status} />
      </div>
      <p style={{ margin: "0.5rem 0", color: "#64748b" }}>{task.description}</p>
      <p>
        <strong>Срок:</strong> {formatDuration(task.duration_minutes)} (до {formatDate(task.due_at)})
      </p>

      {task.completion && (
        <p style={{ marginTop: "0.5rem" }}>
          <strong>Итог:</strong> {task.completion.outcome === "SUCCESS" ? "Успешно" : "Неуспешно"} —{" "}
          {task.completion.comment}
        </p>
      )}

      {task.comments.length > 0 && (
        <div style={{ marginTop: "0.75rem" }}>
          <strong>Комментарии:</strong>
          <ul style={{ paddingLeft: "1rem", marginTop: "0.25rem" }}>
            {task.comments.map((c) => (
              <li key={c.id}>{c.text}</li>
            ))}
          </ul>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      {isActive && (
        <div style={{ marginTop: "1rem" }}>
          {task.status === "ASSIGNED" && (
            <button
              className="btn"
              style={{ marginBottom: "0.75rem" }}
              onClick={() => startTask.mutate()}
              disabled={startTask.isPending}
            >
              Взять в работу
            </button>
          )}

          <form onSubmit={handleComment} style={{ marginBottom: "0.75rem" }}>
            <div className="form-group">
              <label>Комментарий</label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={2}
                placeholder="Добавить комментарий к задаче"
              />
            </div>
            <button className="btn btn-secondary" type="submit" disabled={addComment.isPending}>
              Отправить комментарий
            </button>
          </form>

          <div className="form-group">
            <label>Комментарий при завершении *</label>
            <textarea
              value={completeComment}
              onChange={(e) => setCompleteComment(e.target.value)}
              rows={2}
              placeholder="Обязателен для завершения"
            />
          </div>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button
              className="btn btn-success"
              onClick={() => handleComplete("SUCCESS")}
              disabled={completeTask.isPending}
            >
              Успешно
            </button>
            <button
              className="btn btn-danger"
              onClick={() => handleComplete("FAILURE")}
              disabled={completeTask.isPending}
            >
              Неуспешно
            </button>
          </div>
        </div>
      )}
    </article>
  );
}

export default function EmployeeDashboard() {
  const { user, logout } = useAuth();
  const tasksQuery = useQuery({ queryKey: ["myTasks"], queryFn: api.getMyTasks });
  const tasks = tasksQuery.data ?? [];

  return (
    <div className="app-layout">
      <header className="header">
        <div>
          <h1>Мои задачи</h1>
          <p style={{ color: "#64748b" }}>{user?.full_name}</p>
        </div>
        <button className="btn btn-secondary" onClick={logout}>
          Выйти
        </button>
      </header>

      {tasksQuery.isLoading && <p>Загрузка...</p>}
      <div className="task-grid">
        {tasks.map((task) => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>
      {!tasksQuery.isLoading && tasks.length === 0 && (
        <p style={{ color: "#64748b" }}>Нет назначенных задач</p>
      )}
    </div>
  );
}
