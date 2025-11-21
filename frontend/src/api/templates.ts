import { apiClient } from "./client";
import type { ModelTemplate } from "./types";

export const getModelTemplates = async (): Promise<ModelTemplate[]> => {
  const { data } = await apiClient.get<ModelTemplate[]>("/models/templates");
  return data;
};


