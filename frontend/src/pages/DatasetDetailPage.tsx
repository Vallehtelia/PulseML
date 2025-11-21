import { useEffect, useMemo, useState } from "react";
import type { ChangeEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";

import Card from "@/components/ui/Card";
import Select from "@/components/ui/Select";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import type {
  ColumnRole,
  DatasetColumnMeta,
  DatasetMeta,
} from "@/api/types";
import { getDataset, updateDatasetSchema } from "@/api/datasets";

const roleOptions: ColumnRole[] = ["feature", "target", "timestamp", "ignore"];

const DatasetDetailPage = () => {
  const params = useParams<{ id: string }>();
  const datasetId = Number(params.id);
  const datasetQuery = useQuery({
    queryKey: ["dataset", datasetId],
    queryFn: () => getDataset(datasetId),
    enabled: Number.isFinite(datasetId),
  });

  const [columns, setColumns] = useState<DatasetColumnMeta[]>([]);

  useEffect(() => {
    if (datasetQuery.data?.dataset.meta.columns) {
      setColumns(datasetQuery.data.dataset.meta.columns);
    }
  }, [datasetQuery.data]);

  const updateMutation = useMutation({
    mutationFn: (payload: DatasetColumnMeta[]) =>
      updateDatasetSchema(datasetId, payload.map((col) => ({ name: col.name, role: col.role }))),
    onSuccess: () => datasetQuery.refetch(),
  });

  const dataset = datasetQuery.data?.dataset;
  const preview = datasetQuery.data?.preview ?? [];

  const summary = useMemo(() => dataset?.meta ?? ({} as DatasetMeta), [dataset]);

  if (!dataset) {
    return <Card title="Dataset">Loading dataset...</Card>;
  }

  return (
    <div className="grid" style={{ gap: "1.5rem" }}>
      <Card
        title={dataset.name}
        description={`Uploaded ${new Date(dataset.created_at).toLocaleString()}`}
      >
        <div style={{ display: "flex", gap: "2rem" }}>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Rows</span>
            <div style={{ fontSize: "1.2rem" }}>{summary.n_rows ?? "—"}</div>
          </div>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Columns</span>
            <div style={{ fontSize: "1.2rem" }}>{summary.n_columns ?? "—"}</div>
          </div>
          <div>
            <span style={{ color: "var(--color-text-secondary)" }}>Type</span>
            <div>
              <Badge>{dataset.type}</Badge>
            </div>
          </div>
        </div>
        <div style={{ marginTop: "1rem" }}>
          <Link to={`/training/new?datasetId=${dataset.id}`}>
            <Button>Start new training</Button>
          </Link>
        </div>
      </Card>

      <Card title="Columns">
        <table>
          <thead>
            <tr>
              <th align="left">Column</th>
              <th align="left">dtype</th>
              <th align="left">Role</th>
              <th align="right">Missing %</th>
            </tr>
          </thead>
          <tbody>
            {columns.map((col) => (
              <tr key={col.name}>
                <td>{col.name}</td>
                <td>{col.dtype}</td>
                <td>
                  <Select
                    value={col.role}
                    onChange={(event: ChangeEvent<HTMLSelectElement>) => {
                      const role = event.target.value as ColumnRole;
                      setColumns((current: DatasetColumnMeta[]) =>
                        current.map((item) =>
                          item.name === col.name ? { ...item, role } : item,
                        ),
                      );
                    }}
                  >
                    {roleOptions.map((role) => (
                      <option key={role} value={role}>
                        {role}
                      </option>
                    ))}
                  </Select>
                </td>
                <td align="right">{col.missing_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
        <Button
          style={{ marginTop: "1rem" }}
          onClick={() => updateMutation.mutate(columns)}
          disabled={updateMutation.isPending}
        >
          {updateMutation.isPending ? "Saving..." : "Save schema"}
        </Button>
      </Card>

      <Card title="Preview" description="First 20 rows">
        <div style={{ overflowX: "auto" }}>
          <table>
            <thead>
              <tr>
                {Object.keys(preview[0] ?? {}).map((key) => (
                  <th key={key}>{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview.map((row, index) => (
                <tr key={index}>
                  {Object.keys(preview[0] ?? {}).map((key) => (
                    <td key={key}>{String(row[key] ?? "")}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default DatasetDetailPage;


