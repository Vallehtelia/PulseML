import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import { useAuth } from "@/hooks/useAuth";

const RegisterPage = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await register(email, password);
      navigate("/login");
    } catch (err) {
      setError("Unable to register. Please try a different email.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--color-bg)",
      }}
    >
      <Card
        title="Create PulseML account"
        description="Spin up experiments in minutes"
        className="auth-card"
      >
        <form className="grid" style={{ gap: "1rem", width: "320px" }} onSubmit={handleSubmit}>
          <label className="grid" style={{ gap: "0.5rem" }}>
            <span>Email</span>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <label className="grid" style={{ gap: "0.5rem" }}>
            <span>Password</span>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>
          {error && <span style={{ color: "var(--color-danger)" }}>{error}</span>}
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating..." : "Register"}
          </Button>
          <p style={{ color: "var(--color-text-secondary)", textAlign: "center" }}>
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </form>
      </Card>
    </div>
  );
};

export default RegisterPage;


