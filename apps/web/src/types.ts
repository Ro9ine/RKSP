export type UserRole = "TEAMLEAD" | "EMPLOYEE";

export type TaskStatus = "ASSIGNED" | "IN_PROGRESS" | "COMPLETED" | "FAILED";

export type TaskOutcome = "SUCCESS" | "FAILURE";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  created_at: string;
}

export interface TeamMember {
  id: string;
  user_id: string;
  joined_at: string;
  user: User | null;
}

export interface Team {
  id: string;
  name: string;
  teamlead_id: string;
  created_at: string;
  members: TeamMember[];
}

export interface TaskComment {
  id: string;
  task_id: string;
  author_id: string;
  text: string;
  created_at: string;
  author: User | null;
}

export interface TaskCompletion {
  id: string;
  outcome: TaskOutcome;
  comment: string;
  completed_at: string;
}

export interface Task {
  id: string;
  team_id: string;
  assignee_id: string;
  title: string;
  description: string;
  status: TaskStatus;
  duration_minutes: number;
  due_at: string;
  created_at: string;
  updated_at: string;
  assignee: User | null;
  comments: TaskComment[];
  completion: TaskCompletion | null;
}

export interface ApiError {
  status_code: number;
  message: string;
  errors?: unknown[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
