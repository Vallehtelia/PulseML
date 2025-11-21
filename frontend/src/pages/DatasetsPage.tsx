import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import Button from "@/components/ui/Button";
import DatasetTable from "@/components/domain/DatasetTable";
import DatasetUploadDialog from "@/components/domain/DatasetUploadDialog";
import { getDatasets, uploadDataset } from "@/api/datasets";

const DatasetsPage = () => {
  const [showUpload, setShowUpload] = useState(false);
  const datasetsQuery = useQuery({
    queryKey: ["datasets"],
    queryFn: getDatasets,
  });

  const uploadMutation = useMutation({
    mutationFn: uploadDataset,
    onSuccess: () => datasetsQuery.refetch(),
  });

  return (
    <div className="grid" style={{ gap: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <Button onClick={() => setShowUpload(true)}>Upload dataset</Button>
      </div>
      <DatasetTable datasets={datasetsQuery.data ?? []} />
      <DatasetUploadDialog
        open={showUpload}
        onClose={() => setShowUpload(false)}
        onUpload={(formData) => uploadMutation.mutateAsync(formData)}
      />
    </div>
  );
};

export default DatasetsPage;


