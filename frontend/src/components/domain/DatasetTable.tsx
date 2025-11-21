import { Link } from "react-router-dom";
import type { Dataset } from "@/api/types";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";

type Props = {
  datasets: Dataset[];
};

const DatasetTable = ({ datasets }: Props) => {
  if (!datasets.length) {
    return (
      <Card title="Datasets">
        <p style={{ color: "var(--color-text-secondary)" }}>
          No datasets uploaded yet. Click &ldquo;Upload dataset&rdquo; to get started.
        </p>
      </Card>
    );
  }

  return (
    <Card title="Datasets">
      <table>
        <thead>
          <tr>
            <th align="left">Name</th>
            <th align="left">Type</th>
            <th align="right">Rows</th>
            <th align="right">Columns</th>
            <th align="left">Created</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {datasets.map((dataset) => (
            <tr key={dataset.id}>
              <td>{dataset.name}</td>
              <td>
                <Badge>{dataset.type}</Badge>
              </td>
              <td align="right">{dataset.meta.n_rows ?? "—"}</td>
              <td align="right">{dataset.meta.n_columns ?? "—"}</td>
              <td>{new Date(dataset.created_at).toLocaleString()}</td>
              <td>
                <Link to={`/datasets/${dataset.id}`} style={{ color: "var(--color-primary)" }}>
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

export default DatasetTable;


