import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";

import Card from "@/components/ui/Card";
import Select from "@/components/ui/Select";
import Button from "@/components/ui/Button";
import HyperparamForm from "@/components/domain/HyperparamForm";
import { getDatasets } from "@/api/datasets";
import { getModelTemplates } from "@/api/templates";
import { createTrainingRun } from "@/api/training";

const NewTrainingRunPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialDatasetId = Number(searchParams.get("datasetId")) || undefined;

  const datasetsQuery = useQuery({ queryKey: ["datasets"], queryFn: getDatasets });
  const templatesQuery = useQuery({ queryKey: ["model-templates"], queryFn: getModelTemplates });

  const [datasetId, setDatasetId] = useState<number | undefined>(initialDatasetId);
  const [templateId, setTemplateId] = useState<number | undefined>();
  const [hparams, setHparams] = useState<Record<string, unknown>>({});

  const selectedTemplate = useMemo(
    () => templatesQuery.data?.find((template) => template.id === templateId),
    [templateId, templatesQuery.data],
  );

  useEffect(() => {
    if (selectedTemplate) {
      setHparams(selectedTemplate.default_hparams);
    }
  }, [selectedTemplate]);

  const mutation = useMutation({
    mutationFn: createTrainingRun,
    onSuccess: (run) => navigate(`/training-runs/${run.id}`),
  });

  const canSubmit = Boolean(datasetId && templateId);

  return (
    <Card title="Start a training run" description="Wire datasets to TCN, LSTM, CNN, or Transformer templates">
      <div className="grid" style={{ gap: "1.25rem" }}>
        <label className="grid" style={{ gap: "0.5rem" }}>
          <span>Dataset</span>
          <Select
            value={datasetId ?? ""}
            onChange={(event) => setDatasetId(Number(event.target.value))}
          >
            <option value="">Select dataset</option>
            {(datasetsQuery.data ?? []).map((dataset) => (
              <option key={dataset.id} value={dataset.id}>
                {dataset.name} ({dataset.meta.n_columns ?? "?"} cols)
              </option>
            ))}
          </Select>
        </label>

        <label className="grid" style={{ gap: "0.5rem" }}>
          <span>Model template</span>
          <Select
            value={templateId ?? ""}
            onChange={(event) => setTemplateId(Number(event.target.value))}
          >
            <option value="">Select template</option>
            {(templatesQuery.data ?? []).map((template) => (
              <option key={template.id} value={template.id}>
                {template.name} — {template.task_type}
              </option>
            ))}
          </Select>
        </label>

        {selectedTemplate && (
          <HyperparamForm
            fields={selectedTemplate.hyperparam_schema}
            values={hparams}
            onChange={(key, value) => setHparams((prev) => ({ ...prev, [key]: value }))}
          />
        )}

        <div style={{ display: "flex", gap: "1rem" }}>
          <Button
            onClick={() =>
              mutation.mutate({
                dataset_id: datasetId!,
                model_template_id: templateId!,
                hparams,
              })
            }
            disabled={!canSubmit || mutation.isPending}
          >
            {mutation.isPending ? "Launching..." : "Start training"}
          </Button>
          <Button variant="ghost" onClick={() => navigate("/ai-assistant")}>
            Auto-tune with AI 🤖 (Coming soon)
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default NewTrainingRunPage;


