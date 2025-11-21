import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";

import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import TrainingMetricsChart from "@/components/domain/TrainingMetricsChart";
import { getTrainingMetrics, getTrainingRun, stopTrainingRun } from "@/api/training";

const TrainingRunDetailPage = () => {
  const params = useParams<{ id: string }>();
  const runId = Number(params.id);

  const runQuery = useQuery({
    queryKey: ["training-run", runId],
    queryFn: () => getTrainingRun(runId),
    enabled: Number.isFinite(runId),
    // Poll every 2 seconds if training is running
    refetchInterval: (query) => {
      const run = query.state.data;
      return run?.status === "running" ? 2000 : false;
    },
  });

  const metricsQuery = useQuery({
    queryKey: ["training-run", runId, "metrics"],
    queryFn: () => getTrainingMetrics(runId),
    enabled: Number.isFinite(runId),
    // Poll every 2 seconds if training is running
    refetchInterval: (query) => {
      const run = runQuery.data;
      return run?.status === "running" ? 2000 : false;
    },
  });

  const stopMutation = useMutation({
    mutationFn: () => stopTrainingRun(runId),
    onSuccess: () => runQuery.refetch(),
  });

  const run = runQuery.data;

  if (!run) {
    return <Card title="Training run">Loading run...</Card>;
  }

  const canStop = ["pending", "queued", "running"].includes(run.status);

  return (
    <div className="grid" style={{ gap: "1.5rem" }}>
      <Card
        title={`Run #${run.id}`}
        description={
          <span>
            Dataset{" "}
            <Link to={`/datasets/${run.dataset_id}`} style={{ color: "var(--color-primary)" }}>
              #{run.dataset_id}
            </Link>
          </span>
        }
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div style={{ display: "flex", gap: "2rem", alignItems: "center", flexWrap: "wrap" }}>
            <Badge>{run.status}</Badge>
            {run.device && (
              <div>
                <strong>Device:</strong>{" "}
                <Badge variant={run.device === "cuda" ? "success" : "default"}>
                  {run.device.toUpperCase()}
                </Badge>
              </div>
            )}
            {run.status === "running" && run.current_epoch !== null && run.total_epochs !== null && (
              <div>
                <strong>Progress:</strong> Epoch {run.current_epoch} / {run.total_epochs} (
                {Math.round((run.current_epoch / run.total_epochs) * 100)}%)
                <div
                  style={{
                    width: "200px",
                    height: "8px",
                    background: "var(--color-surface-alt)",
                    borderRadius: "4px",
                    marginTop: "0.25rem",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: `${(run.current_epoch / run.total_epochs) * 100}%`,
                      height: "100%",
                      background: "var(--color-primary)",
                      transition: "width 0.3s ease",
                    }}
                  />
                </div>
              </div>
            )}
            <div>
              <strong>Best metric:</strong>{" "}
              {run.best_metric_name ? `${run.best_metric_name}: ${run.best_metric_value ?? "—"}` : "—"}
            </div>
          </div>
          {canStop && (
            <div>
              <Button variant="danger" onClick={() => stopMutation.mutate()} disabled={stopMutation.isPending}>
                {stopMutation.isPending ? "Stopping..." : "Stop run"}
              </Button>
            </div>
          )}
        </div>
      </Card>

      <Card title="Hyperparameters">
        <table>
          <tbody>
            {Object.entries(run.hparams ?? {}).map(([key, value]) => (
              <tr key={key}>
                <td>{key}</td>
                <td>{Array.isArray(value) ? value.join(", ") : String(value)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <TrainingMetricsChart metrics={metricsQuery.data ?? null} />

      <Card title="Artifacts">
        <p style={{ color: "var(--color-text-secondary)" }}>
          Model weights & logs will appear here when the training engine ships in Phase 3.
        </p>
      </Card>
    </div>
  );
};

export default TrainingRunDetailPage;


