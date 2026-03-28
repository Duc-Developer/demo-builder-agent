export type TodoItem = {
  id: string;
  title: string;
  completed: boolean;
  createdAt: number;
  updatedAt: number;
};

export type Filter = "all" | "active" | "completed";

export type State = {
  todos: TodoItem[];
  filter: Filter;
  searchQuery: string;
  editingId?: string;
  error: string | null;
};

