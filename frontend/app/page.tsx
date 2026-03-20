"use client";

import Image from "next/image";
import { FormEvent, useMemo, useState } from "react";
import ThemeToggle from "@/components/theme-toggle";

type ToolResult = {
  tool: string;
  query: string;
  results: Array<Record<string, unknown>>;
};

type SourceItem = {
  title: string;
  url: string;
  snippet?: string;
  type?: string;
};

type ResearchResponse = {
  status?: string;
  plan?: string[];
  logs?: string[];
  final_report?: string;
  sources?: SourceItem[];
  tool_results?: ToolResult[];
};

type ProgressEvent = {
  node: string;
  label: string;
  status: string;
  plan_count: number;
  source_count: number;
  last_log: string;
  timestamp: number;
};

type StreamPlanEvent = {
  index: number;
  text: string;
  total: number;
};

type StreamSourceEvent = {
  index: number;
  total: number;
  title: string;
  url: string;
  snippet?: string;
  type?: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8001";
const SAMPLE_QUERY =
  "Research the impact of AI on software engineering jobs from 2023 to 2026. Include key findings, risks, and recommendations with sources.";
const WORKFLOW_STEPS = [
  { node: "planner_node", label: "Planning" },
  { node: "memory_retrieve_node", label: "Retrieving Memory" },
  { node: "research_node", label: "Researching Sources" },
  { node: "summarize_node", label: "Generating Draft" },
  { node: "critic_node", label: "Revising Report" },
  { node: "memory_store_node", label: "Storing Memory" }
];

export default function Home() {
  type Stage = "idle" | "in_progress" | "completed";
  const [query, setQuery] = useState(SAMPLE_QUERY);
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [error, setError] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [stage, setStage] = useState<Stage>("idle");
  const [progress, setProgress] = useState<ProgressEvent[]>([]);
  const [livePlan, setLivePlan] = useState<string[]>([]);
  const [liveSources, setLiveSources] = useState<SourceItem[]>([]);
  const [liveLogs, setLiveLogs] = useState<string[]>([]);

  const reportText = useMemo(() => result?.final_report?.trim() ?? "", [result]);
  const planItems = livePlan.length ? livePlan : result?.plan ?? [];
  const sourceItems = liveSources.length ? liveSources : result?.sources ?? [];
  const logItems = liveLogs.length ? liveLogs : result?.logs ?? [];
  const stageLabel = stage === "in_progress" ? "In Progress" : stage === "completed" ? "Completed" : "Idle";
  const stageClass =
    stage === "in_progress"
      ? "stage-pill--in-progress"
      : stage === "completed"
        ? "stage-pill--completed"
        : "stage-pill--idle";
  const progressByNode = useMemo(() => {
    return new Map(progress.map((item) => [item.node, item]));
  }, [progress]);
  const activeNode = useMemo(() => {
    if (!isRunning) return null;
    const completedNodes = WORKFLOW_STEPS.filter((step) => progressByNode.has(step.node));
    if (!completedNodes.length) return WORKFLOW_STEPS[0]?.node ?? null;

    const lastCompletedNode = completedNodes[completedNodes.length - 1];
    const completedIdx = WORKFLOW_STEPS.findIndex((step) => step.node === lastCompletedNode.node);
    const nextStep = WORKFLOW_STEPS[completedIdx + 1];
    return nextStep?.node ?? lastCompletedNode.node;
  }, [isRunning, progressByNode]);

  const runResearch = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const cleanQuery = query.trim();
    if (!cleanQuery) {
      setError("Please enter a research query.");
      return;
    }

    setError("");
    setIsRunning(true);
    setStage("in_progress");
    setResult(null);
    setProgress([]);
    setLivePlan([]);
    setLiveSources([]);
    setLiveLogs([]);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/research/stream?query=${encodeURIComponent(cleanQuery)}`,
        {
          method: "GET",
          headers: { Accept: "text/event-stream" }
        }
      );

      if (!response.ok) {
        const body = (await response.json().catch(() => null)) as
          | { detail?: string }
          | null;
        throw new Error(body?.detail ?? `Request failed (${response.status})`);
      }

      if (!response.body) {
        throw new Error("Streaming not supported by this browser.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let gotDone = false;

      const applyEvent = (eventName: string, rawData: string) => {
        let payload: unknown = null;
        try {
          payload = rawData ? JSON.parse(rawData) : null;
        } catch {
          payload = null;
        }

        if (eventName === "status") {
          return;
        }

        if (eventName === "progress") {
          const item = (payload ?? {}) as Partial<ProgressEvent>;
          const next: ProgressEvent = {
            node: item.node ?? "unknown",
            label: item.label ?? item.node ?? "Working",
            status: item.status ?? "running",
            plan_count: item.plan_count ?? 0,
            source_count: item.source_count ?? 0,
            last_log: item.last_log ?? "",
            timestamp: Date.now()
          };

          setProgress((prev) => {
            const idx = prev.findIndex((p) => p.node === next.node);
            if (idx === -1) return [...prev, next];
            const copy = [...prev];
            copy[idx] = next;
            return copy;
          });
          return;
        }

        if (eventName === "plan") {
          const item = (payload ?? {}) as Partial<StreamPlanEvent>;
          const stepText = (item.text ?? "").trim();
          if (!stepText) return;

          setLivePlan((prev) => {
            if (prev.includes(stepText)) return prev;
            return [...prev, stepText];
          });
          return;
        }

        if (eventName === "source") {
          const item = (payload ?? {}) as Partial<StreamSourceEvent>;
          const nextSource: SourceItem = {
            title: item.title ?? "",
            url: item.url ?? "",
            snippet: item.snippet ?? "",
            type: item.type ?? "web"
          };

          if (!nextSource.url && !nextSource.title) return;

          setLiveSources((prev) => {
            const key = `${nextSource.title}|${nextSource.url}`;
            const exists = prev.some((s) => `${s.title}|${s.url}` === key);
            if (exists) return prev;
            return [...prev, nextSource];
          });
          return;
        }

        if (eventName === "log") {
          const item = (payload ?? {}) as { text?: string };
          const line = (item.text ?? "").trim();
          if (!line) return;
          setLiveLogs((prev) => (prev[prev.length - 1] === line ? prev : [...prev, line]));
          return;
        }

        if (eventName === "result") {
          const finalResult = (payload ?? null) as ResearchResponse | null;
          setResult(finalResult);
          if (finalResult) {
            setLivePlan((prev) => (prev.length ? prev : finalResult.plan ?? []));
            setLiveSources((prev) => (prev.length ? prev : finalResult.sources ?? []));
            setLiveLogs((prev) => (prev.length ? prev : finalResult.logs ?? []));
          }
          return;
        }

        if (eventName === "error") {
          const p = (payload ?? {}) as { message?: string };
          setError(p.message ?? "Stream failed.");
          return;
        }

        if (eventName === "done") {
          gotDone = true;
          setStage("completed");
        }
      };

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        while (true) {
          const boundary = buffer.indexOf("\n\n");
          if (boundary === -1) break;

          const block = buffer.slice(0, boundary);
          buffer = buffer.slice(boundary + 2);

          let eventName = "message";
          const dataLines: string[] = [];

          for (const line of block.split("\n")) {
            if (line.startsWith("event:")) {
              eventName = line.slice(6).trim();
            } else if (line.startsWith("data:")) {
              dataLines.push(line.slice(5).trim());
            }
          }

          applyEvent(eventName, dataLines.join("\n"));
        }

        if (gotDone) {
          await reader.cancel();
          break;
        }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error occurred.";
      setError(message);
      setStage("idle");
    } finally {
      setIsRunning(false);
    }
  };

  const downloadMarkdown = () => {
    if (!reportText) return;
    const blob = new Blob([reportText], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ara_report.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadPdf = async () => {
    if (!reportText) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/research/pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: "ARA Research Report",
          markdown_text: reportText
        })
      });

      if (!response.ok) {
        throw new Error(`PDF export failed (${response.status})`);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "ara_report.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to export PDF.";
      setError(message);
    }
  };

  return (
    <main className="page-shell">
      <div className="glow glow-a" aria-hidden />
      <div className="glow glow-b" aria-hidden />

      <section className="card">
        <header className="card-head">
          <div className="brand">
            <Image src="/next.svg" alt="Next.js logo" width={26} height={26} />
            <div>
              <p className="eyebrow">Native Next.js Frontend</p>
              <h1>Autonomous Research Agent</h1>
            </div>
          </div>
          <ThemeToggle />
        </header>

        <p className="lede">
          Run autonomous research directly from the UI and pull results from FastAPI.
        </p>

        <div className="status-row">
          <span className="pill">Frontend: 3001</span>
          <span className="pill">Backend: {API_BASE_URL}</span>
          <span className={`stage-pill ${stageClass} is-active`} aria-label="Run status">
            <span className="stage-dot" aria-hidden />
            {stageLabel}
          </span>
        </div>

        <form className="query-form" onSubmit={runResearch}>
          <label className="input-label" htmlFor="research-query">
            Research Query
          </label>
          <textarea
            id="research-query"
            className="query-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your research prompt..."
            rows={5}
          />
          <div className="button-row">
            <button className="btn btn-primary" type="submit" disabled={isRunning}>
              {isRunning ? "Running..." : "Run Research"}
            </button>
            <button
              className="btn"
              type="button"
              disabled={!reportText}
              onClick={downloadMarkdown}
            >
              Download Markdown
            </button>
            <button
              className="btn"
              type="button"
              disabled={!reportText}
              onClick={downloadPdf}
            >
              Download PDF
            </button>
          </div>
        </form>

        {error ? <p className="error-box">{error}</p> : null}

        {result || isRunning || progress.length ? (
          <section className="result-grid">
            <article className="panel panel-wide">
              <h2>Live Progress</h2>
              <ul className="timeline">
                {WORKFLOW_STEPS.map((step) => {
                  const item = progressByNode.get(step.node);
                  const isCompleted = Boolean(item);
                  const isActive = !isCompleted && isRunning && activeNode === step.node;
                  const checkState = isCompleted
                    ? "timeline-check--completed"
                    : isActive
                      ? "timeline-check--active"
                      : "timeline-check--pending";

                  return (
                    <li key={step.node}>
                      <div className="timeline-left">
                        <span className={`timeline-check ${checkState}`} aria-hidden>
                          {isCompleted || isActive ? "✓" : ""}
                        </span>
                        <span className="timeline-label">{step.label}</span>
                      </div>
                      <span className="timeline-meta">
                        plan {item?.plan_count ?? 0} | sources {item?.source_count ?? 0}
                      </span>
                    </li>
                  );
                })}
              </ul>
            </article>

            <article className="panel">
              <h2>Plan</h2>
              {planItems.length ? (
                <ol>
                  {planItems.map((step, idx) => (
                    <li key={`${idx}-${step}`}>{step}</li>
                  ))}
                </ol>
              ) : (
                <p className="muted">No plan generated.</p>
              )}
            </article>

            <article className="panel">
              <h2>Sources</h2>
              {sourceItems.length ? (
                <ul>
                  {sourceItems.map((source, idx) => (
                    <li key={`${idx}-${source.url}-${source.title}`}>
                      <a href={source.url} target="_blank" rel="noreferrer">
                        {source.title || source.url}
                      </a>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">No sources available.</p>
              )}
            </article>

            <article className="panel panel-wide">
              <h2>Final Report</h2>
              {reportText ? (
                <pre className="report-block">{reportText}</pre>
              ) : (
                <p className="muted">No report generated.</p>
              )}
            </article>

            <article className="panel panel-wide">
              <h2>Logs</h2>
              {logItems.length ? (
                <pre className="log-block">{logItems.join("\n")}</pre>
              ) : (
                <p className="muted">No logs available.</p>
              )}
            </article>
          </section>
        ) : null}
      </section>
    </main>
  );
}
