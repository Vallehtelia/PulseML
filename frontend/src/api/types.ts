export type ColumnRole = "feature" | "target" | "timestamp" | "ignore";

export interface DatasetColumnMeta {
  name: string;
  dtype: string;
  missing_pct: number;
  role: ColumnRole;
  stats?: Record<string, number | null>;
}

export interface DatasetMeta {
  n_rows?: number;
  n_columns?: number;
  columns: DatasetColumnMeta[];
  suggested_roles: Record<string, ColumnRole>;
}

export interface Dataset {
  id: number;
  owner_id: number;
  name: string;
  description?: string | null;
  type: string;
  meta: DatasetMeta;
  created_at: string;
}

export interface DatasetPreview {
  dataset: Dataset;
  preview: Record<string, unknown>[];
}

export interface ColumnRoleUpdate {
  name: string;
  role: ColumnRole;
}

export interface TrainingRun {
  id: number;
  owner_id: number;
  dataset_id: number;
  model_template_id: number;
  status: string;
  hparams: Record<string, unknown>;
  best_metric_name?: string | null;
  best_metric_value?: number | null;
  model_checkpoint_path?: string | null;
  logs_path?: string | null;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
  error_message?: string | null;
}

export interface TrainingMetric {
  run_id: number;
  metrics: { step?: number; epoch?: number; value?: number; name?: string }[];
}

export interface HyperParamField {
  key: string;
  label: string;
  type: string;
  default: unknown;
  min?: number;
  max?: number;
  options?: unknown[];
  info?: string;
}

export interface ModelTemplate {
  id: number;
  name: string;
  task_type: string;
  default_hparams: Record<string, unknown>;
  hyperparam_schema: HyperParamField[];
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserProfile {
  id: number;
  email: string;
  created_at: string;
}


