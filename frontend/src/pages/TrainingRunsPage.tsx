import { useQuery } from "@tanstack/react-query";
import TrainingRunList from "@/components/domain/TrainingRunList";
import { getTrainingRuns } from "@/api/training";

const TrainingRunsPage = () => {
  const runsQuery = useQuery({
    queryKey: ["training-runs"],
    queryFn: getTrainingRuns,
  });

  return <TrainingRunList runs={runsQuery.data ?? []} />;
};

export default TrainingRunsPage;


