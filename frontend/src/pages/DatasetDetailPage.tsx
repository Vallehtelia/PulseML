import { useEffect, useMemo, useState } from "react";
import type { ChangeEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";

import Card from "@/components/ui/Card";
import Select from "@/components/ui/Select";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import Input from "@/components/ui/Input";
import type {
  ColumnRole,
  DatasetColumnMeta,
  DatasetMeta,
} from "@/api/types";
import { deleteDataset, getDataset, renameDataset, updateDatasetSchema } from "@/api/datasets";

const roleOptions: ColumnRole[] = ["feature", "target", "timestamp", "ignore"];

const DatasetDetailPage = () => {
  const params = useParams<{ id: string }>();
  const navigate = useNavigate();
  const datasetId = Number(params.id);
  const datasetQuery = useQuery({
    queryKey: ["dataset", datasetId],
    queryFn: () => getDataset(datasetId),
    enabled: Number.isFinite(datasetId),
  });

  const [columns, setColumns] = useState<DatasetColumnMeta[]>([]);
  const [isEditingName, setIsEditingName] = useState(false);
  const [editedName, setEditedName] = useState("");
  const [editedDescription, setEditedDescription] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const dataset = datasetQuery.data?.dataset;
  const preview = datasetQuery.data?.preview ?? [];

  useEffect(() => {
    if (datasetQuery.data?.dataset.meta.columns) {
      setColumns(datasetQuery.data.dataset.meta.columns);
    }
  }, [datasetQuery.data]);

  useEffect(() => {
    if (dataset) {
      setEditedName(dataset.name);
      setEditedDescription(dataset.description || "");
    }
  }, [dataset]);

  const updateMutation = useMutation({
    mutationFn: (payload: DatasetColumnMeta[]) =>
      updateDatasetSchema(datasetId, payload.map((col) => ({ name: col.name, role: col.role }))),
    onSuccess: () => datasetQuery.refetch(),
  });

  const renameMutation = useMutation({
    mutationFn: () => renameDataset(datasetId, editedName, editedDescription || null),
    onSuccess: () => {
      datasetQuery.refetch();
      setIsEditingName(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteDataset(datasetId),
    onSuccess: () => {
      navigate("/datasets");
    },
  });

  const summary = useMemo(() => dataset?.meta ?? ({} as DatasetMeta), [dataset]);

  if (!dataset) {
    return <Card title="Dataset">Loading dataset...</Card>;
  }

  return (
    <div className="grid" style={{ gap: "1.5rem" }}>
      <Card
        title={
          isEditingName ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <Input
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                placeholder="Dataset name"
              />
              <Input
                value={editedDescription}
                onChange={(e) => setEditedDescription(e.target.value)}
                placeholder="Description (optional)"
              />
            </div>
          ) : (
            dataset.name
          )
        }
        description={
          isEditingName
            ? undefined
            : dataset.description || `Uploaded ${new Date(dataset.created_at).toLocaleString()}`
        }
      >
        <div style={{ display: "grid", gap: "1rem" }}>
          {/* Stats Section */}
          <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap" }}>
            <div>
              <span style={{ color: "var(--color-text-secondary)", fontSize: "0.875rem" }}>Rows</span>
              <div style={{ fontSize: "1.2rem", fontWeight: 600 }}>{summary.n_rows ?? "—"}</div>
            </div>
            <div>
              <span style={{ color: "var(--color-text-secondary)", fontSize: "0.875rem" }}>Columns</span>
              <div style={{ fontSize: "1.2rem", fontWeight: 600 }}>{summary.n_columns ?? "—"}</div>
            </div>
            <div>
              <span style={{ color: "var(--color-text-secondary)", fontSize: "0.875rem" }}>Type</span>
              <div style={{ marginTop: "0.25rem" }}>
                <Badge>{dataset.type}</Badge>
              </div>
            </div>
          </div>

          {/* Actions Section */}
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            {isEditingName ? (
              <>
                <Button
                  onClick={() => renameMutation.mutate()}
                  disabled={renameMutation.isPending || !editedName.trim()}
                >
                  {renameMutation.isPending ? "Saving..." : "Save"}
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setIsEditingName(false);
                    setEditedName(dataset.name);
                    setEditedDescription(dataset.description || "");
                  }}
                  disabled={renameMutation.isPending}
                >
                  Cancel
                </Button>
              </>
            ) : (
              <>
                <Link to={`/training/new?datasetId=${dataset.id}`}>
                  <Button>Start new training</Button>
                </Link>
                <Button variant="secondary" onClick={() => setIsEditingName(true)}>
                  Rename
                </Button>
                <Button variant="danger" onClick={() => setShowDeleteConfirm(true)}>
                  Delete
                </Button>
              </>
            )}
          </div>
        </div>
      </Card>

      <Card title="Columns">
        <div style={{ overflowX: "auto" }}>
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
        </div>
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

      {showDeleteConfirm && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
          onClick={() => setShowDeleteConfirm(false)}
        >
          <Card
            title="Delete Dataset"
            style={{ maxWidth: "500px", margin: "1rem" }}
            onClick={(e) => e.stopPropagation()}
          >
            <p style={{ marginBottom: "1.5rem" }}>
              Are you sure you want to delete <strong>{dataset.name}</strong>? This action cannot be undone.
            </p>
            <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
              <Button variant="secondary" onClick={() => setShowDeleteConfirm(false)}>
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={() => {
                  deleteMutation.mutate();
                  setShowDeleteConfirm(false);
                }}
                disabled={deleteMutation.isPending}
              >
                {deleteMutation.isPending ? "Deleting..." : "Delete"}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default DatasetDetailPage;


