import { apiClient } from "./client";
import type { TrainingMetric, TrainingRun } from "./types";

export interface TrainingRunCreatePayload {
  dataset_id: number;
  model_template_id: number;
  hparams: Record<string, unknown>;
}

export const getTrainingRuns = async (): Promise<TrainingRun[]> => {
  const { data } = await apiClient.get<TrainingRun[]>("/training-runs");
  return data;
};

export const getTrainingRun = async (id: number): Promise<TrainingRun> => {
  const { data } = await apiClient.get<TrainingRun>(`/training-runs/${id}`);
  return data;
};

export const createTrainingRun = async (
  payload: TrainingRunCreatePayload,
): Promise<TrainingRun> => {
  const { data } = await apiClient.post<TrainingRun>("/training-runs", payload);
  return data;
};

export const getTrainingMetrics = async (id: number): Promise<TrainingMetric> => {
  const { data } = await apiClient.get<TrainingMetric>(`/training-runs/${id}/metrics`);
  return data;
};

export const stopTrainingRun = async (id: number): Promise<TrainingRun> => {
  const { data } = await apiClient.post<TrainingRun>(`/training-runs/${id}/stop`);
  return data;
};


