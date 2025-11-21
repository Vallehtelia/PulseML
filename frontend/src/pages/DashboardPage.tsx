import { Link } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";

import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import DatasetTable from "@/components/domain/DatasetTable";
import TrainingRunList from "@/components/domain/TrainingRunList";
import DatasetUploadDialog from "@/components/domain/DatasetUploadDialog";
import { getDatasets, uploadDataset } from "@/api/datasets";
import { getTrainingRuns } from "@/api/training";
import { useState } from "react";

const DashboardPage = () => {
  const datasetsQuery = useQuery({
    queryKey: ["datasets"],
    queryFn: getDatasets,
  });
  const runsQuery = useQuery({
    queryKey: ["training-runs"],
    queryFn: getTrainingRuns,
  });
  const [showUpload, setShowUpload] = useState(false);

  const uploadMutation = useMutation({
    mutationFn: uploadDataset,
    onSuccess: () => datasetsQuery.refetch(),
  });

  const datasetCount = datasetsQuery.data?.length ?? 0;
  const runCount = runsQuery.data?.length ?? 0;

  return (
    <div className="grid" style={{ gap: "1.5rem" }}>
      <section className="grid" style={{ gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: "1rem" }}>
        <Card title="Datasets" description={`${datasetCount} total`}>
          <Button variant="ghost" onClick={() => setShowUpload(true)}>
            Upload dataset
          </Button>
        </Card>
        <Card title="Training runs" description={`${runCount} total`}>
          <Link to="/training/new">
            <Button variant="ghost">Start new training</Button>
          </Link>
        </Card>
        <Card title="AI assistant" description="Coming soon">
          <Link to="/ai-assistant">
            <Button variant="ghost">Preview assistant</Button>
          </Link>
        </Card>
      </section>

      <DatasetTable datasets={(datasetsQuery.data ?? []).slice(0, 3)} />
      <TrainingRunList runs={(runsQuery.data ?? []).slice(0, 3)} />

      <DatasetUploadDialog
        open={showUpload}
        onClose={() => setShowUpload(false)}
        onUpload={async (formData) => uploadMutation.mutateAsync(formData)}
      />
    </div>
  );
};

export default DashboardPage;


