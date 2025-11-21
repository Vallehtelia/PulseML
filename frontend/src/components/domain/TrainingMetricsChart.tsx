import {
  Legend,
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

  // Transform data to show train_loss and val_loss
  const chartData = data.map((point: any) => ({
    epoch: point.epoch ?? point.step ?? 0,
    train_loss: point.train_loss ?? null,
    val_loss: point.val_loss ?? null,
  }));

  return (
    <Card title="Training Metrics">
      {!data.length ? (
        <p style={{ color: "var(--color-text-secondary)" }}>
          No metrics available yet. Metrics will appear as training progresses.
        </p>
      ) : (
        <div style={{ width: "100%", height: 400 }}>
          <ResponsiveContainer>
            <LineChart
              data={chartData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <XAxis
                dataKey="epoch"
                label={{ value: "Epoch", position: "insideBottom", offset: -5 }}
                type="number"
                scale="linear"
                domain={["dataMin", "dataMax"]}
              />
              <YAxis
                label={{ value: "Loss", angle: -90, position: "insideLeft" }}
                type="number"
                scale="linear"
              />
              <RechartsTooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="train_loss"
                stroke="#2563EB"
                strokeWidth={2.5}
                name="Train Loss"
                dot={false}
                activeDot={{ r: 4 }}
                connectNulls={false}
              />
              <Line
                type="monotone"
                dataKey="val_loss"
                stroke="#DC2626"
                strokeWidth={2.5}
                name="Validation Loss"
                dot={false}
                activeDot={{ r: 4 }}
                connectNulls={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
};

export default TrainingMetricsChart;


