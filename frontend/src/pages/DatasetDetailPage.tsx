import { useEffect, useMemo, useState } from "react";
import type { ChangeEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";

import Card from "@/components/ui/Card";
import Select from "@/components/ui/Select";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import Input from "@/components/ui/Input";
import Modal from "@/components/ui/Modal";
import type {
  ColumnRole,
  DatasetColumnMeta,
  DatasetMeta,
} from "@/api/types";
import {
  createTargetColumn,
  deleteDataset,
  getDataset,
  renameDataset,
  updateDatasetSchema,
} from "@/api/datasets";

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
  const [showTargetModal, setShowTargetModal] = useState(false);

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

  const createTargetMutation = useMutation({
    mutationFn: (sourceColumn: string) =>
      createTargetColumn(datasetId, sourceColumn, "target"),
    onSuccess: () => {
      setShowTargetModal(false);
      // Refetch to get the updated dataset with new column
      datasetQuery.refetch();
    },
  });

  const setTargetColumn = (columnName: string) => {
    // Check if target already exists
    if (columns.some((col) => col.role === "target")) {
      setShowTargetModal(false);
      return;
    }
    // Create new target column by copying the source column
    createTargetMutation.mutate(columnName);
  };

  // Filter columns that can be used as target (numeric columns, not timestamp)
  const targetableColumns = columns.filter(
    (col) =>
      (col.dtype === "float64" || col.dtype === "int64") &&
      col.role !== "timestamp" &&
      col.role !== "ignore"
  );

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
                  variant="ghost"
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
                <Button variant="ghost" onClick={() => setIsEditingName(true)}>
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
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", flexWrap: "wrap" }}>
          <Button
            variant="ghost"
            onClick={() => setShowTargetModal(true)}
            disabled={targetableColumns.length === 0 || columns.some((col) => col.role === "target")}
          >
            {columns.some((col) => col.role === "target")
              ? "Target Already Set"
              : "Set Target Column"}
          </Button>
          {columns.some((col) => col.role === "target") && (
            <Badge variant="success">
              Target: {columns.find((col) => col.role === "target")?.name}
            </Badge>
          )}
        </div>
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

      <Modal
        title="Set Target Column"
        open={showTargetModal}
        onClose={() => setShowTargetModal(false)}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {columns.some((col) => col.role === "target") ? (
            <div
              style={{
                padding: "1rem",
                background: "var(--color-warning)",
                borderRadius: "0.5rem",
                color: "#000",
              }}
            >
              <strong>Target already set:</strong>{" "}
              {columns.find((col) => col.role === "target")?.name}
              <br />
              <span style={{ fontSize: "0.875rem", marginTop: "0.5rem", display: "block" }}>
                To change the target, first set the current target column's role to "feature" in the
                table above, then come back here.
              </span>
            </div>
          ) : (
            <p style={{ margin: 0, color: "var(--color-text-secondary)" }}>
              Select a column to use as the target (the value to predict):
            </p>
          )}
          <div
            style={{
              maxHeight: "400px",
              overflowY: "auto",
              border: "1px solid var(--color-border)",
              borderRadius: "0.5rem",
              padding: "0.5rem",
            }}
          >
            {targetableColumns.length === 0 ? (
              <p style={{ margin: 0, color: "var(--color-text-secondary)", padding: "1rem" }}>
                No suitable columns found. Target columns must be numeric (float64 or int64).
              </p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                {targetableColumns.map((col) => {
                  const hasTarget = columns.some((c) => c.role === "target");
                  return (
                    <button
                      key={col.name}
                      onClick={() => !hasTarget && setTargetColumn(col.name)}
                      disabled={hasTarget}
                      style={{
                        padding: "0.75rem",
                        textAlign: "left",
                        background: hasTarget ? "var(--color-surface-alt)" : "transparent",
                        border: "1px solid var(--color-border)",
                        borderRadius: "0.25rem",
                        cursor: hasTarget ? "not-allowed" : "pointer",
                        color: hasTarget ? "var(--color-text-secondary)" : "var(--color-text)",
                        opacity: hasTarget ? 0.6 : 1,
                        transition: "all 0.2s",
                      }}
                      onMouseEnter={(e) => {
                        if (!hasTarget) {
                          e.currentTarget.style.background = "var(--color-surface-hover)";
                          e.currentTarget.style.borderColor = "var(--color-primary)";
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!hasTarget) {
                          e.currentTarget.style.background = "transparent";
                          e.currentTarget.style.borderColor = "var(--color-border)";
                        }
                      }}
                    >
                      <div style={{ fontWeight: 500 }}>{col.name}</div>
                      <div
                        style={{
                          fontSize: "0.875rem",
                          color: "var(--color-text-secondary)",
                          marginTop: "0.25rem",
                        }}
                      >
                        {col.dtype} • {col.missing_pct}% missing
                        {col.role === "target" && (
                          <span style={{ marginLeft: "0.5rem" }}>
                            <Badge variant="success">Current target</Badge>
                          </span>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
            <Button variant="ghost" onClick={() => setShowTargetModal(false)}>
              Cancel
            </Button>
          </div>
        </div>
      </Modal>

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
          <div onClick={(e) => e.stopPropagation()}>
            <Card title="Delete Dataset" style={{ maxWidth: "500px", margin: "1rem" }}>
            <p style={{ marginBottom: "1.5rem" }}>
              Are you sure you want to delete <strong>{dataset.name}</strong>? This action cannot be undone.
            </p>
            <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
              <Button variant="ghost" onClick={() => setShowDeleteConfirm(false)}>
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
        </div>
      )}
    </div>
  );
};

export default DatasetDetailPage;


