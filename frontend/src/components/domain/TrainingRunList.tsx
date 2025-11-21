import { Link } from "react-router-dom";
import type { TrainingRun } from "@/api/types";
import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";

const statusVariant = (status: string) => {
  switch (status) {
    case "completed":
      return "success";
    case "failed":
      return "danger";
    case "running":
    case "queued":
      return "warning";
    default:
      return "default";
  }
};

type Props = {
  runs: TrainingRun[];
};

const TrainingRunList = ({ runs }: Props) => {
  if (!runs.length) {
    return (
      <Card title="Training runs">
        <p style={{ color: "var(--color-text-secondary)" }}>
          No runs yet. Launch your first experiment to see progress here.
        </p>
      </Card>
    );
  }

  return (
    <Card title="Training runs">
      <table>
        <thead>
          <tr>
            <th align="left">Run ID</th>
            <th align="left">Status</th>
            <th align="right">Best metric</th>
            <th align="left">Created</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.id}>
              <td>#{run.id}</td>
              <td>
                <Badge variant={statusVariant(run.status)}>{run.status}</Badge>
              </td>
              <td align="right">
                {run.best_metric_name
                  ? `${run.best_metric_name}: ${run.best_metric_value ?? "—"}`
                  : "—"}
              </td>
              <td>{new Date(run.created_at).toLocaleString()}</td>
              <td>
                <Link
                  to={`/training-runs/${run.id}`}
                  style={{ color: "var(--color-primary)" }}
                >
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
};

export default TrainingRunList;


