import Card from "@/components/ui/Card";

const AIAssistantInfoPage = () => {
  return (
    <Card title="AI Hyperparameter Assistant – coming soon">
      <p>
        PulseML is preparing an AI copilot that will analyze your historical training
        runs, study the best and worst hyperparameter sets, and iteratively suggest
        improved configurations until improvements plateau.
      </p>
      <ul>
        <li>Review every training run and surface the strongest signals.</li>
        <li>Compare high-performing and underperforming hyperparameters.</li>
        <li>Propose new hparam sets, enqueue runs, and learn from the results.</li>
        <li>Stop automatically once improvements flatten out.</li>
      </ul>
      <p style={{ color: "var(--color-text-secondary)" }}>
        For Phase 2 you control every hyperparameter manually. Stay tuned for the PulseML
        AI assistant in Phase 3.
      </p>
    </Card>
  );
};

export default AIAssistantInfoPage;


