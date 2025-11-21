import { useRef, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import Modal from "@/components/ui/Modal";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";

type Props = {
  open: boolean;
  onClose: () => void;
  onUpload: (formData: FormData) => Promise<unknown>;
};

const DatasetUploadDialog = ({ open, onClose, onUpload }: Props) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [datasetName, setDatasetName] = useState("");
  const [description, setDescription] = useState("");
  const fileRef = useRef<HTMLInputElement | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!fileRef.current?.files?.length) return;
    const file = fileRef.current.files[0];
    const formData = new FormData();
    formData.append("file", file);
    formData.append("name", datasetName);
    formData.append("description", description);
    setIsSubmitting(true);
    try {
      await onUpload(formData);
      setDatasetName("");
      setDescription("");
      if (fileRef.current) {
        fileRef.current.value = "";
      }
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal title="Upload dataset" open={open} onClose={onClose}>
      <form onSubmit={handleSubmit} className="grid" style={{ gap: "1rem" }}>
        <label className="grid" style={{ gap: "0.5rem" }}>
          <span>Dataset name</span>
          <Input
            placeholder="Solar demand history..."
            value={datasetName}
            onChange={(event: ChangeEvent<HTMLInputElement>) =>
              setDatasetName(event.target.value)
            }
            required
          />
        </label>
        <label className="grid" style={{ gap: "0.5rem" }}>
          <span>Description (optional)</span>
          <Input
            placeholder="Peak demand forecasting dataset"
            value={description}
            onChange={(event: ChangeEvent<HTMLInputElement>) =>
              setDescription(event.target.value)
            }
          />
        </label>
        <label className="grid" style={{ gap: "0.5rem" }}>
          <span>CSV file</span>
          <Input type="file" accept=".csv" ref={fileRef} required />
        </label>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Uploading..." : "Upload"}
        </Button>
      </form>
    </Modal>
  );
};

export default DatasetUploadDialog;


