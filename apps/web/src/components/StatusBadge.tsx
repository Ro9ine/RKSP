import type { TaskStatus } from "../types";

const labels: Record<TaskStatus, string> = {
  ASSIGNED: "Назначена",
  IN_PROGRESS: "В работе",
  COMPLETED: "Выполнена",
  FAILED: "Не выполнена",
};

const classes: Record<TaskStatus, string> = {
  ASSIGNED: "badge badge-assigned",
  IN_PROGRESS: "badge badge-progress",
  COMPLETED: "badge badge-completed",
  FAILED: "badge badge-failed",
};

export default function StatusBadge({ status }: { status: TaskStatus }) {
  return <span className={classes[status]}>{labels[status]}</span>;
}
