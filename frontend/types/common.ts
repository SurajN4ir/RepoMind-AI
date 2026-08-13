export type DeepPartial<T> = T extends object
  ? { [P in keyof T]?: DeepPartial<T[P]> }
  : T;

export type Nullable<T> = T | null;

export type AsyncState<T> =
  | { status: "idle"; data?: never; error?: never }
  | { status: "loading"; data?: never; error?: never }
  | { status: "success"; data: T; error?: never }
  | { status: "error"; data?: never; error: string };

export type PaginatedResponse<T> = {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
};

export type ApiError = {
  detail: string;
  code?: string;
  status?: number;
};
