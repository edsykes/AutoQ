import { useEffect, useState } from "react";

type Health = { status: string; database: string };

export function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => setError(true));
  }, []);

  return (
    <main style={{ fontFamily: "system-ui", maxWidth: 480, margin: "4rem auto" }}>
      <h1>AutoQ</h1>
      <p data-testid="api-health">
        API health: {error ? "unreachable" : health ? health.status : "checking…"}
      </p>
      {health && <p>Database: {health.database}</p>}
    </main>
  );
}
