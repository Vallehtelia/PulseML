import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  XAxis,
  YAxis,
} from "recharts";
import Card from "@/components/ui/Card";
import type { TrainingMetric } from "@/api/types";

type Props = {
  metrics?: TrainingMetric | null;
};

const TrainingMetricsChart = ({ metrics }: Props) => {
  const data = metrics?.metrics ?? [];

  return (
    <Card title="Metrics">
      {!data.length ? (
        <p style={{ color: "var(--color-text-secondary)" }}>
          No metrics available yet (training engine arrives in Phase 3).
        </p>
      ) : (
        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer>
            <LineChart
              data={data.map((point, index) => ({
                step: point.epoch ?? point.step ?? index,
                value: point.value ?? 0,
              }))}
            >
              <XAxis dataKey="step" />
              <YAxis />
              <RechartsTooltip />
              <Line type="monotone" dataKey="value" stroke="#2563EB" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
};

export default TrainingMetricsChart;


