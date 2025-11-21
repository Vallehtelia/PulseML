import { apiClient } from "./client";
import type {
  ColumnRoleUpdate,
  Dataset,
  DatasetPreview,
} from "./types";

export const getDatasets = async (): Promise<Dataset[]> => {
  const { data } = await apiClient.get<Dataset[]>("/datasets");
  return data;
};

export const getDataset = async (id: number): Promise<DatasetPreview> => {
  const { data } = await apiClient.get<DatasetPreview>(`/datasets/${id}`);
  return data;
};

export const uploadDataset = async (form: FormData): Promise<DatasetPreview> => {
  const { data } = await apiClient.post<DatasetPreview>("/datasets/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};

export const updateDatasetSchema = async (
  datasetId: number,
  columns: ColumnRoleUpdate[],
): Promise<Dataset> => {
  const { data } = await apiClient.put<Dataset>(`/datasets/${datasetId}/schema`, {
    columns,
  });
  return data;
};

export const renameDataset = async (
  datasetId: number,
  name: string,
  description?: string | null,
): Promise<Dataset> => {
  const { data } = await apiClient.patch<Dataset>(`/datasets/${datasetId}`, {
    name,
    description,
  });
  return data;
};

export const deleteDataset = async (datasetId: number): Promise<void> => {
  await apiClient.delete(`/datasets/${datasetId}`);
};


