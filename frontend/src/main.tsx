import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { Editor, type EditorHandle } from "./Editor";
import "./style.css";

type Span = { start: number; end: number; start_line: number; start_column: number; end_line: number; end_column: number };
type Diagnostic = { code: string; stage: string; severity: string; message: string; hint?: string; span?: Span };
type CompileResult = {
  compiler_version: string; source_hash: string; translatable: boolean; tokens: Array<Record<string, any>>;
  ast: Record<string, any> | null; symbols: Array<Record<string, any>>; diagnostics: Diagnostic[];
  phases: Record<string, { status: string; duration_ms: number }>; artifacts: Record<string, { source: string; artifact_hash: string; source_map?: Array<{ generated_line: number; source_span: Span }> }>;
};
type Project = { id: string; name: string; source: string; source_hash: string; version: number; updated_at: string };
type NavTab = "editor" | "translate" | "console" | "tests" | "projects" | "defense" | "help";
type Run = { run_id: string; target: string; status: string; stdout: string; stderr: string; exit_code: number | null; duration_ms: number; error_code: string | null; source_hash: string; artifact_hash: string; runtime_version: string };
type EditableTestCase = { id: string; inputs: string; expected_stdout: string };

const API = "/api/v1";
const STARTER = `Inicio
Leer numero
Escribir "Resultado: ", numero * 2
Fin
`;
const INVALID_SAMPLE = "Inicio\nEscribir @\nFin\n";
const labels: Record<NavTab, string> = {
  editor: "Editor", translate: "Traducción", console: "Consola", tests: "Pruebas",
  projects: "Proyectos", defense: "Defensa", help: "Ayuda",
};
const exampleTitles: Record<string, string> = {
  A: "Operaciones aritméticas", B: "Condicional anidado", C: "Para y acumuladores",
  D: "Arreglos 1-based", E: "Funciones y retorno",
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
  });
  const body = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    const detail = body?.detail;
    const message = detail?.message ?? detail?.code ?? body?.error?.code ?? `HTTP ${response.status}`;
    const error = new Error(message) as Error & { detail?: unknown; status?: number };
    error.detail = detail;
    error.status = response.status;
    throw error;
  }
  return body as T;
}

function downloadText(name: string, content: string, mime = "text/plain;charset=utf-8") {
  const url = URL.createObjectURL(new Blob([content], { type: mime }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  URL.revokeObjectURL(url);
}

function App() {
  const [tab, setTab] = useState<NavTab>("editor");
  const [source, setSource] = useState(() => localStorage.getItem("pseudo-studio:draft") ?? STARTER);
  const [analysis, setAnalysis] = useState<CompileResult | null>(null);
  const [analysisRevision, setAnalysisRevision] = useState(-1);
  const [translation, setTranslation] = useState<CompileResult | null>(null);
  const [translationRevision, setTranslationRevision] = useState(-1);
  const [selectedInspector, setSelectedInspector] = useState<"tokens" | "ast" | "symbols" | "diagnostics" | "phases">("tokens");
  const [revision, setRevision] = useState(0);
  const [health, setHealth] = useState<Record<string, any> | null>(null);
  const [busy, setBusy] = useState("");
  const [notice, setNotice] = useState("");
  const [examples, setExamples] = useState<Array<{ id: string; title: string }>>([]);
  const [project, setProject] = useState<Project | null>(null);
  const [projectName, setProjectName] = useState("Sin título");
  const [projectState, setProjectState] = useState("Borrador local");
  const [projects, setProjects] = useState<Project[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [batchInputs, setBatchInputs] = useState("");
  const [consoleText, setConsoleText] = useState("");
  const [interactiveInput, setInteractiveInput] = useState("");
  const [inputRequested, setInputRequested] = useState(false);
  const [activeRunId, setActiveRunId] = useState("");
  const [report, setReport] = useState<Record<string, any> | null>(null);
  const [exampleId, setExampleId] = useState("A");
  const [testCases, setTestCases] = useState<EditableTestCase[]>([
    { id: "propio-1", inputs: "4\n2\n3", expected_stdout: "Ingrese el primer número:\nIngrese el segundo número:\nIngrese el tercer número:\nEl resultado es: 16\n" },
  ]);
  const [grammar, setGrammar] = useState("");
  const [defenseCase, setDefenseCase] = useState<"valid" | "invalid">("valid");
  const [defenseStep, setDefenseStep] = useState(-1);
  const [defenseLog, setDefenseLog] = useState<Array<{ phase: string; result: string; source_hash?: string }>>([]);
  const editorRef = useRef<EditorHandle>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const autoSaveTimer = useRef<number | undefined>(undefined);
  const sourceWasEdited = useRef(false);
  const sourceIsStale = analysis !== null && analysisRevision !== revision;
  const translationIsStale = translation !== null && translationRevision !== revision;
  const currentCompileInvalid = analysis !== null && analysisRevision === revision && !analysis.translatable;

  const setSourceChanged = useCallback((value: string) => {
    sourceWasEdited.current = true;
    setSource(value);
    setRevision((current) => current + 1);
    setProjectState("Cambios pendientes");
    setNotice("");
    localStorage.setItem("pseudo-studio:draft", value);
  }, []);

  const analyze = useCallback(async () => {
    setBusy("analyze");
    setNotice("");
    try {
      const result = await request<CompileResult>("/analyze", { method: "POST", body: JSON.stringify({ source }) });
      setAnalysis(result);
      setAnalysisRevision(revision);
      setSelectedInspector(result.diagnostics.length ? "diagnostics" : "tokens");
      setNotice(result.translatable ? `Análisis completo · ${result.tokens.length} tokens · ${result.source_hash.slice(0, 12)}` : `${result.diagnostics.length} diagnóstico(s) · ${result.source_hash.slice(0, 12)}`);
      return result;
    } catch (error) {
      setNotice(`No se pudo analizar: ${(error as Error).message}`);
      return null;
    } finally {
      setBusy("");
    }
  }, [source, revision]);

  const translate = useCallback(async () => {
    setBusy("translate");
    setNotice("");
    try {
      const result = await request<CompileResult>("/translate", {
        method: "POST", body: JSON.stringify({ source, targets: ["python", "javascript"] }),
      });
      setTranslation(result);
      setTranslationRevision(revision);
      setAnalysis(result);
      setAnalysisRevision(revision);
      setTab("translate");
      setNotice(`Dos destinos generados · fuente ${result.source_hash.slice(0, 12)}`);
      return result;
    } catch (error) {
      const detail = (error as Error & { detail?: any }).detail;
      if (detail?.diagnostics) {
        setAnalysis({
          compiler_version: "", source_hash: detail.source_hash, translatable: false,
          tokens: [], ast: null, symbols: [], diagnostics: detail.diagnostics, phases: {}, artifacts: {},
        });
        setAnalysisRevision(revision);
        setSelectedInspector("diagnostics");
      }
      setNotice(`Traducción bloqueada: ${(error as Error).message}`);
      return null;
    } finally {
      setBusy("");
    }
  }, [source, revision]);

  const refreshHealth = useCallback(async () => {
    try {
      const value = await request<Record<string, any>>("/health");
      setHealth(value);
    } catch (error) {
      setHealth({ status: "offline", error: (error as Error).message, components: {} });
    }
  }, []);

  const refreshProjects = useCallback(async () => {
    try {
      const response = await request<{ projects: Project[] }>("/projects");
      setProjects(response.projects);
    } catch (error) {
      setNotice(`No se pudieron cargar los proyectos: ${(error as Error).message}`);
    }
  }, []);

  useEffect(() => {
    void refreshHealth();
    void refreshProjects();
    void request<{ examples: Array<{ id: string; title: string }> }>("/examples")
      .then((result) => setExamples(result.examples))
      .catch((error) => setNotice(`No se cargó la biblioteca oficial: ${(error as Error).message}`));
    void fetch(`${API}/grammar`).then((response) => response.ok ? response.text() : "").then(setGrammar).catch(() => setGrammar(""));
    if (!localStorage.getItem("pseudo-studio:draft")) {
      void request<{ source: string }>("/examples/A").then((result) => {
        if (sourceWasEdited.current) return;
        setSource(result.source);
        localStorage.setItem("pseudo-studio:draft", result.source);
      }).catch(() => undefined);
    }
    const healthTimer = window.setInterval(() => void refreshHealth(), 15_000);
    return () => window.clearInterval(healthTimer);
  }, [refreshHealth, refreshProjects]);

  useEffect(() => {
    const dirty = projectState === "Cambios pendientes" || projectState === "Guardando…";
    const warn = (event: BeforeUnloadEvent) => {
      if (!dirty) return;
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [projectState]);

  useEffect(() => {
    if (!project || (project.source === source && project.name === projectName)) return;
    setProjectState("Cambios pendientes");
    window.clearTimeout(autoSaveTimer.current);
    autoSaveTimer.current = window.setTimeout(async () => {
      setProjectState("Guardando…");
      try {
        const updated = await request<Project>(`/projects/${project.id}`, {
          method: "PUT", body: JSON.stringify({ name: projectName, source, version: project.version }),
        });
        setProject(updated);
        setProjectState("Guardado automáticamente");
        void refreshProjects();
      } catch (error) {
        setProjectState((error as Error & { status?: number }).status === 409 ? "Conflicto al guardar" : "Error al guardar");
        setNotice(`No se guardó el proyecto: ${(error as Error).message}. Vuelve a cargar la lista para resolverlo.`);
      }
    }, 900);
    return () => window.clearTimeout(autoSaveTimer.current);
  }, [source, project, projectName, refreshProjects]);

  const loadExample = async (id: string) => {
    setBusy("example");
    try {
      const result = await request<{ source: string; cases: Array<{ inputs: string[]; expected_stdout: string }> }>(`/examples/${id}`);
      setExampleId(id);
      setSourceChanged(result.source);
      if (result.cases[0]) {
        setBatchInputs(result.cases[0].inputs.join("\n"));
        setTestCases((current) => current.map((item, index) => index === 0 ? {
          ...item, inputs: result.cases[0].inputs.join("\n"), expected_stdout: result.cases[0].expected_stdout,
        } : item));
      }
      setProject(null);
      setProjectName(`${id} · ${exampleTitles[id]}`);
      setProjectState("Ejemplo académico · no guardado");
      setAnalysis(null);
      setTranslation(null);
      setNotice(`Se abrió ${id} desde los fixtures académicos originales.`);
    } catch (error) {
      setNotice(`No se pudo abrir ${id}: ${(error as Error).message}`);
    } finally {
      setBusy("");
    }
  };

  const runBatch = async (target: "python" | "javascript") => {
    const inputs = batchInputs === "" ? [] : batchInputs.replace(/\r/g, "").split("\n");
    const runId = crypto.randomUUID().replaceAll("-", "");
    setBusy(`run-${target}`);
    setActiveRunId(runId);
    setTab("console");
    setConsoleText(`${target === "python" ? "Python 3" : "Node.js"} · ejecutando en sandbox…\n`);
    try {
      const result = await request<Run>("/run", {
        method: "POST", body: JSON.stringify({ source, target, inputs: { values: inputs }, run_id: runId, project_id: project?.id }),
      });
      setRuns((current) => [result, ...current.filter((item) => item.run_id !== result.run_id)]);
      setConsoleText(`${result.stdout}${result.stderr ? `\n[stderr]\n${result.stderr}` : ""}\n${result.status} · exit ${result.exit_code} · ${result.duration_ms.toFixed(1)} ms · ${result.runtime_version}\nSHA-256 ${result.source_hash}`);
      setActiveRunId("");
      if (result.status !== "completed") setNotice(`La ejecución terminó con estado ${result.status} (${result.error_code ?? "sin código"}).`);
      else setNotice(`Ejecución ${target} correcta · ${result.duration_ms.toFixed(1)} ms.`);
      void refreshProjects();
    } catch (error) {
      setConsoleText(`Ejecución no disponible: ${(error as Error).message}`);
      setActiveRunId("");
      setNotice(`No se pudo ejecutar: ${(error as Error).message}`);
    } finally {
      setBusy("");
    }
  };

  const startInteractive = async (target: "python" | "javascript") => {
    const wsUrl = `${location.protocol === "https:" ? "wss:" : "ws:"}//${location.host}/api/v1/run/interactive`;
    const socket = new WebSocket(wsUrl);
    wsRef.current = socket;
    setTab("console");
    setBusy(`interactive-${target}`);
    setInputRequested(false);
    setConsoleText(`${target === "python" ? "Python 3" : "Node.js"} · iniciando sesión interactiva…\n`);
    socket.onopen = () => socket.send(JSON.stringify({ type: "start", source, target }));
    socket.onmessage = (message) => {
      const event = JSON.parse(message.data) as Record<string, any>;
      if (event.event === "started") {
        setActiveRunId(event.run_id);
        setConsoleText((text) => text + `Fuente ${event.source_hash}\n`);
      } else if (event.event === "stdout") {
        setConsoleText((text) => text + event.data);
      } else if (event.event === "stderr") {
        setConsoleText((text) => text + `[stderr] ${event.data}`);
      } else if (event.event === "input_requested") {
        setInputRequested(true);
        setNotice(`El programa solicita entrada ${event.input_type === "TEXT" ? "de texto" : "numérica"}.`);
      } else if (event.event === "exited") {
        setRuns((current) => [event as Run, ...current]);
        setConsoleText((text) => text + `\n${event.status} · exit ${event.exit_code} · ${Number(event.duration_ms).toFixed(1)} ms\nSHA-256 ${event.source_hash}`);
        setActiveRunId("");
        setInputRequested(false);
        setBusy("");
        wsRef.current = null;
        void refreshProjects();
      } else if (event.event === "error") {
        const diagnosticText = event.diagnostics?.map((item: Diagnostic) => `${item.code}: ${item.message}`).join("\n") ?? event.message ?? event.code;
        setConsoleText((text) => text + `\nError: ${diagnosticText}\n`);
        setNotice(`Sesión interactiva: ${event.code}`);
        setBusy("");
        setInputRequested(false);
      }
    };
    socket.onerror = () => {
      setConsoleText((text) => text + "\nNo se pudo conectar al WebSocket local.\n");
      setBusy("");
    };
    socket.onclose = () => {
      if (wsRef.current === socket) {
        wsRef.current = null;
        setBusy("");
        setInputRequested(false);
      }
    };
  };

  const cancelRun = async () => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ type: "cancel" }));
      setNotice("Cancelación solicitada al runtime.");
      return;
    }
    if (!activeRunId) return;
    for (let attempt = 0; attempt < 20; attempt += 1) {
      try {
        await request(`/runs/${activeRunId}/cancel`, { method: "POST" });
        setNotice("Cancelación solicitada al contenedor.");
        return;
      } catch (error) {
        if ((error as Error & { status?: number }).status === 404 && attempt < 19) {
          await new Promise((resolve) => window.setTimeout(resolve, 100));
          continue;
        }
        setNotice(`No se pudo cancelar: ${(error as Error).message}`);
        return;
      }
    }
  };

  const sendInteractiveInput = (event: React.FormEvent) => {
    event.preventDefault();
    if (!wsRef.current || !inputRequested) return;
    wsRef.current.send(JSON.stringify({ type: "input", value: interactiveInput }));
    setConsoleText((text) => text + `\n> ${interactiveInput}\n`);
    setInteractiveInput("");
    setInputRequested(false);
  };

  const saveNewProject = async () => {
    const name = window.prompt("Nombre del proyecto", projectName || "Mi programa");
    if (!name?.trim()) return;
    setBusy("save-project");
    try {
      const created = await request<Project>("/projects", { method: "POST", body: JSON.stringify({ name, source }) });
      setProject(created);
      setProjectName(created.name);
      setProjectState("Guardado");
      setNotice(`Proyecto “${created.name}” guardado en la base local.`);
      void refreshProjects();
    } catch (error) {
      setNotice(`No se pudo guardar: ${(error as Error).message}`);
    } finally {
      setBusy("");
    }
  };

  const saveProject = async () => {
    if (!project) return saveNewProject();
    setBusy("save-project");
    try {
      const updated = await request<Project>(`/projects/${project.id}`, {
        method: "PUT", body: JSON.stringify({ name: projectName, source, version: project.version }),
      });
      setProject(updated);
      setProjectState("Guardado");
      setNotice(`Cambios guardados · versión ${updated.version}.`);
      void refreshProjects();
    } catch (error) {
      setProjectState("Error al guardar");
      setNotice(`No se pudo guardar el proyecto: ${(error as Error).message}`);
    } finally {
      setBusy("");
    }
  };

  const openProject = async (id: string) => {
    try {
      const opened = await request<Project>(`/projects/${id}`);
      const history = await request<{ runs: Run[] }>(`/projects/${id}/runs`);
      setProject(opened);
      setProjectName(opened.name);
      setSourceChanged(opened.source);
      setProjectState("Guardado");
      setAnalysis(null);
      setTranslation(null);
      setRuns(history.runs);
      setNotice(`Proyecto abierto · revisión ${opened.version}.`);
    } catch (error) {
      setNotice(`No se pudo abrir el proyecto: ${(error as Error).message}`);
    }
  };

  const duplicateProject = async () => {
    if (!project) return;
    try {
      const copy = await request<Project>(`/projects/${project.id}/duplicate`, { method: "POST" });
      setProject(copy);
      setProjectName(copy.name);
      setSourceChanged(copy.source);
      setProjectState("Guardado");
      await refreshProjects();
      setNotice(`Se creó “${copy.name}”.`);
    } catch (error) {
      setNotice(`No se pudo duplicar: ${(error as Error).message}`);
    }
  };

  const duplicateProjectById = async (id: string) => {
    try {
      const copy = await request<Project>(`/projects/${id}/duplicate`, { method: "POST" });
      await refreshProjects();
      setNotice(`Proyecto duplicado como ${copy.name}.`);
    } catch (error) {
      setNotice(`No se pudo duplicar: ${(error as Error).message}`);
    }
  };

  const deleteProject = async (item: Project) => {
    if (!window.confirm(`¿Eliminar “${item.name}” de la base local?`)) return;
    try {
      await request(`/projects/${item.id}`, { method: "DELETE" });
      if (project?.id === item.id) {
        setProject(null);
        setProjectState("Borrador local");
      }
      await refreshProjects();
      setNotice(`Proyecto “${item.name}” eliminado.`);
    } catch (error) {
      setNotice(`No se pudo eliminar: ${(error as Error).message}`);
    }
  };

  const runTests = async (official: boolean) => {
    setBusy("tests");
    setReport(null);
    setTab("tests");
    try {
      const payload = official
        ? { example_id: exampleId }
        : { source, test_cases: testCases.map((item, index) => ({
            id: item.id.trim() || `propio-${index + 1}`,
            inputs: item.inputs === "" ? [] : item.inputs.replace(/\r/g, "").split("\n"),
            expected_stdout: item.expected_stdout,
          })) };
      const result = await request<Record<string, any>>("/tests/run", { method: "POST", body: JSON.stringify(payload) });
      setReport(result);
      setNotice(`Suite ejecutada en ambos runtimes · ${result.passed}/${result.total} aprobadas.`);
    } catch (error) {
      setNotice(`No se pudo ejecutar la suite: ${(error as Error).message}`);
    } finally {
      setBusy("");
    }
  };

  const exportArtifact = async (kind: string, contentSource = source, reportId?: string) => {
    try {
      const result = await request<{ url: string; filename: string }>("/exports", {
        method: "POST", body: JSON.stringify(reportId ? { kind, report_id: reportId } : { kind, source: contentSource }),
      });
      const response = await fetch(result.url);
      if (!response.ok) throw new Error(`Descarga HTTP ${response.status}`);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = result.filename;
      anchor.click();
      URL.revokeObjectURL(url);
      setNotice(`Descargado ${result.filename}.`);
    } catch (error) {
      setNotice(`No se pudo exportar: ${(error as Error).message}`);
    }
  };

  const runDefenseStep = async () => {
    const step = defenseStep + 1;
    const phaseNames = ["Léxico", "Sintaxis", "Semántica", "Generación", "Ejecución"];
    const phase = phaseNames[step % phaseNames.length];
    setBusy("defense");
    try {
      let result: string;
      let sourceHash: string | undefined;
      if (step % phaseNames.length < 3) {
        const analyzed = await request<CompileResult>("/analyze", { method: "POST", body: JSON.stringify({ source }) });
        sourceHash = analyzed.source_hash;
        result = step % phaseNames.length === 0
          ? `${analyzed.tokens.length} tokens; fase ${analyzed.phases.lexical?.status ?? "sin estado"}`
          : step % phaseNames.length === 1
            ? `${analyzed.ast ? analyzed.ast.kind : "AST no disponible"}; ${analyzed.phases.syntax?.status ?? "sin estado"}`
            : `${analyzed.symbols.length} símbolos; ${analyzed.diagnostics.length} diagnósticos semánticos/compilación`;
        setAnalysis(analyzed);
        setAnalysisRevision(revision);
        if (analyzed.diagnostics.length) setSelectedInspector("diagnostics");
      } else if (step % phaseNames.length === 3) {
        const generated = await request<CompileResult>("/translate", { method: "POST", body: JSON.stringify({ source, targets: ["python", "javascript"] }) });
        sourceHash = generated.source_hash;
        result = `Artefactos reales · Python ${generated.artifacts.python.artifact_hash.slice(0, 12)} · JS ${generated.artifacts.javascript.artifact_hash.slice(0, 12)}`;
        setTranslation(generated);
        setTranslationRevision(revision);
      } else {
        const executed = await request<Run>("/run", {
          method: "POST", body: JSON.stringify({ source, target: "python", inputs: { values: batchInputs ? batchInputs.split("\n") : [] } }),
        });
        sourceHash = executed.source_hash;
        result = `${executed.status} · exit ${executed.exit_code} · stdout: ${JSON.stringify(executed.stdout)}`;
        setRuns((current) => [executed, ...current]);
      }
      setDefenseStep(step);
      setDefenseLog((current) => [...current, { phase, result, source_hash: sourceHash }]);
      setNotice(`Defensa · fase ${phase} completada con respuesta real del servicio.`);
    } catch (error) {
      const result = (error as Error).message;
      setDefenseStep(step);
      setDefenseLog((current) => [...current, { phase, result }]);
      setNotice(`Defensa · ${phase}: ${result}`);
    } finally {
      setBusy("");
    }
  };

  const focusSpan = (span?: Span) => {
    if (!span) return;
    editorRef.current?.focusSpan(span.start, span.end);
    setTab("editor");
  };

  const healthStatus = health?.status ?? "checking";
  const sandboxStatus = health?.components?.sandbox?.available && health?.components?.sandbox_verification?.available;
  const activePhaseLabel = useMemo(() => {
    if (!analysis || analysisRevision !== revision) return "Sin análisis actual";
    return Object.entries(analysis.phases).map(([name, phase]) => `${name} ${phase.status}`).join(" · ");
  }, [analysis, analysisRevision, revision]);

  return <div className="app-shell">
    <header className="topbar">
      <a className="brand" href="#editor" onClick={(event) => { event.preventDefault(); setTab("editor"); }} aria-label="Pseudo Studio inicio">
        <span className="brand-mark">P</span><span>Pseudo<span className="brand-slash"> / </span>Studio</span>
      </a>
      <div className="workspace-title"><span className="eyebrow">ESPACIO LOCAL</span><strong>{projectName || "Sin título"}</strong></div>
      <div className="header-actions">
        <span className={`status-pill ${healthStatus}`} aria-live="polite"><i />API {healthStatus === "ready" ? "lista" : healthStatus === "offline" ? "desconectada" : healthStatus}</span>
        <button className="button button-quiet" onClick={() => void refreshHealth()} aria-label="Actualizar estado">↻ Estado</button>
        <button className="button button-dark" onClick={() => void saveProject()} disabled={busy === "save-project"}>{projectState === "Guardado automáticamente" ? "✓ Guardado" : "Guardar"}</button>
      </div>
    </header>

    <nav className="main-nav" aria-label="Secciones de trabajo">
      {(Object.keys(labels) as NavTab[]).map((key) => <button key={key} className={`nav-item ${tab === key ? "active" : ""}`} onClick={() => setTab(key)} aria-current={tab === key ? "page" : undefined}>
        {labels[key]}{key === "editor" && analysis?.diagnostics?.length ? <span className="nav-count">{analysis.diagnostics.length}</span> : null}
      </button>)}
      <span className="nav-spacer" />
      <span className={`sandbox-indicator ${sandboxStatus ? "online" : "offline"}`}><i />{sandboxStatus ? "Sandbox verificado" : "Sandbox no disponible"}</span>
    </nav>

    {notice && <div className="notice" role="status"><span>{notice}</span><button aria-label="Cerrar aviso" onClick={() => setNotice("")}>×</button></div>}

    <main className="page-content">
      {tab === "editor" && <section className="workbench">
        <div className="section-heading">
          <div><div className="eyebrow">COMPILADOR LOCAL · {project?.name ?? "BORRADOR"}</div><h1>Escribe en pseudocódigo.</h1><p>Analiza la fuente actual y sigue cada paso hasta los runtimes.</p></div>
          <div className="heading-actions">
            <label className="select-wrap"><span className="sr-only">Abrir ejemplo académico</span><select value={exampleId} onChange={(event) => void loadExample(event.target.value)} aria-label="Abrir ejemplo académico" disabled={busy === "example"}>
              {examples.map((item) => <option key={item.id} value={item.id}>{item.id} · {exampleTitles[item.id] ?? item.title}</option>)}
            </select><b>⌄</b></label>
            <button className="button button-light" onClick={() => void analyze()} disabled={Boolean(busy)}>{busy === "analyze" ? "Analizando…" : "◎ Analizar"}</button>
            <button className="button button-accent" onClick={() => void translate()} disabled={Boolean(busy) || currentCompileInvalid} title={currentCompileInvalid ? "Corrige los diagnósticos antes de traducir." : undefined}>{busy === "translate" ? "Generando…" : "Traducir ↗"}</button>
          </div>
        </div>
        <div className="editor-layout">
          <section className="panel editor-panel" aria-label="Editor fuente">
            <div className="panel-bar"><div className="file-tab"><span className="file-icon">⌘</span>{project?.name ? `${project.name}.psc` : "programa.psc"}<span className="dirty-dot" title={projectState}>{projectState === "Guardado" || projectState === "Guardado automáticamente" ? "" : "●"}</span></div>
              <div className="panel-bar-actions"><span className="language-badge">PSEUDOCÓDIGO</span><label className="upload-button" title="Abrir archivo local">Abrir archivo<input type="file" accept=".psc,.txt" onChange={async (event) => {
                const file = event.currentTarget.files?.[0];
                if (!file) return;
                if (file.size > 1_000_000) { setNotice("El archivo supera el límite de 1 MB."); event.currentTarget.value = ""; return; }
                setSourceChanged(await file.text()); setProject(null); setProjectName(file.name.replace(/\.(psc|txt)$/i, "")); setProjectState("Archivo local · borrador");
                event.currentTarget.value = "";
              }} /></label>
              </div>
            </div>
            <div className="editor-body"><Editor ref={editorRef} value={source} onChange={setSourceChanged} /></div>
            <div className="editor-footer"><span>{source.split("\n").length} líneas · {new TextEncoder().encode(source).length.toLocaleString("es")}/1 MB</span><span>{sourceIsStale ? "Análisis desactualizado" : analysis ? `SHA ${analysis.source_hash.slice(0, 12)}` : "Sin analizar"}</span></div>
          </section>

          <section className="panel inspector-panel" aria-label="Inspector del compilador">
            <div className="inspector-header"><div><div className="eyebrow">INSPECTOR</div><h2>Pipeline</h2></div><button className="icon-button" onClick={() => void analyze()} title="Actualizar inspector" aria-label="Actualizar inspector">↻</button></div>
            <div className="inspector-tabs" role="tablist" aria-label="Resultados del análisis">
              {(["tokens", "ast", "symbols", "diagnostics", "phases"] as const).map((panel) => <button role="tab" aria-selected={selectedInspector === panel} className={selectedInspector === panel ? "selected" : ""} key={panel} onClick={() => setSelectedInspector(panel)}>{panel === "symbols" ? "Símbolos" : panel === "diagnostics" ? "Errores" : panel === "phases" ? "Fases" : panel === "ast" ? "AST" : "Tokens"}{panel === "diagnostics" && analysis?.diagnostics.length ? <span className="tab-count">{analysis.diagnostics.length}</span> : null}</button>)}
            </div>
            <div className="inspector-content" role="tabpanel">
              {sourceIsStale && <div className="stale-banner">La fuente cambió. Vuelve a analizar para actualizar estos datos.</div>}
              {!analysis && <div className="empty-state"><span className="empty-symbol">⌁</span><strong>Resultados calculados por el compilador</strong><p>Pulsa «Analizar» para obtener tokens, AST, símbolos y diagnósticos desde la API local.</p></div>}
              {analysis && selectedInspector === "tokens" && <div className="token-table"><div className="mini-table-head"><span>{analysis.tokens.length} tokens</span><span>línea:columna</span></div>{analysis.tokens.map((token: any, index) => <button key={`${token.span?.start}-${index}`} className="token-row" onClick={() => focusSpan(token.span)}><code>{token.lexeme || "∅"}</code><span className={`token-kind kind-${String(token.kind).toLowerCase()}`}>{token.kind}</span><small>{token.span?.start_line}:{token.span?.start_column}</small></button>)}</div>}
              {analysis && selectedInspector === "ast" && <div className="tree-view"><AstNode node={analysis.ast} onSelect={focusSpan} depth={0} /></div>}
              {analysis && selectedInspector === "symbols" && <div className="symbol-list">{analysis.symbols.map((symbol: any) => <button className="symbol-card" key={`${symbol.scope}-${symbol.name}`} onClick={() => focusSpan(symbol.declaration_span)}><div><strong>{symbol.name}</strong><span className="type-chip">{symbol.type ?? symbol.kind}</span></div><small>{symbol.scope} · {symbol.reads} lecturas · {symbol.writes} escrituras · {symbol.initialized ? "inicializada" : "sin inicializar"}</small></button>)}{!analysis.symbols.length && <p className="muted empty-line">No se encontraron símbolos.</p>}</div>}
              {analysis && selectedInspector === "diagnostics" && <div className="diagnostic-list">{analysis.diagnostics.map((item, index) => <button className="diagnostic-card" key={`${item.code}-${index}`} onClick={() => focusSpan(item.span)}><span className="diagnostic-code">{item.code} · {item.stage}</span><strong>{item.message}</strong><small>{item.span ? `Línea ${item.span.start_line}, columna ${item.span.start_column}` : "Sin ubicación"}</small>{item.hint && <p>{item.hint}</p>}</button>)}{!analysis.diagnostics.length && <div className="success-state">✓ Sin diagnósticos para la fuente analizada.</div>}</div>}
              {analysis && selectedInspector === "phases" && <div className="phase-list"><div className="phase-summary">{activePhaseLabel}</div>{Object.entries(analysis.phases).map(([name, phase]) => <div className="phase-row" key={name}><span className={`phase-dot ${phase.status}`} /><div><strong>{name}</strong><small>{phase.status}</small></div><b>{phase.duration_ms.toFixed(2)} ms</b></div>)}<div className="hash-card"><span>SHA-256 de fuente</span><code>{analysis.source_hash}</code><small>Compilador {analysis.compiler_version}</small></div></div>}
            </div>
            <div className="inspector-footer"><span>{analysis ? `Fuente ${analysis.source_hash.slice(0, 12)}` : "API de análisis"}</span><button className="text-button" onClick={() => void exportArtifact(selectedInspector)}>Exportar JSON ↓</button></div>
          </section>
        </div>
        <div className="quick-actions"><div className="quick-copy"><span className="quick-icon">◇</span><div><strong>Runtime aislado</strong><small>{sandboxStatus ? "OCI · sin red · cuotas activas" : "Consulta el estado del sandbox"}</small></div></div>
          <div className="quick-buttons"><button className="button button-light" onClick={() => void runBatch("python")} disabled={!sandboxStatus || Boolean(busy)}>▶ Ejecutar Python</button><button className="button button-light" onClick={() => void runBatch("javascript")} disabled={!sandboxStatus || Boolean(busy)}>▶ Ejecutar JavaScript</button><button className="button button-quiet" onClick={() => setTab("console")}>Consola ↗</button></div>
        </div>
      </section>}

      {tab === "translate" && <section className="subpage">
        <div className="section-heading"><div><div className="eyebrow">GENERACIÓN DESDE AST VALIDADO</div><h1>Dos destinos, una fuente.</h1><p>{translation ? `Hash de entrada ${translation.source_hash}` : "Traduce el texto actual a código ejecutable y autocontenido."}{translationIsStale && <strong className="stale-inline"> · desactualizado</strong>}</p></div><div className="heading-actions"><button className="button button-light" onClick={() => void translate()} disabled={Boolean(busy)}>↻ Generar código</button><button className="button button-accent" onClick={() => void exportArtifact("source")}>Descargar .psc ↓</button></div></div>
        {!translation && <div className="empty-card"><strong>Generación pendiente</strong><p>El backend valida la fuente, construye el AST y genera los dos artefactos a partir de él.</p><button className="button button-accent" onClick={() => void translate()} disabled={Boolean(busy) || currentCompileInvalid}>Traducir fuente actual</button></div>}
        {translation && <div className="code-comparison">
          <article className="panel code-pane source-pane">
            <div className="code-pane-head"><div><span className="runtime-icon source-icon">PSC</span><strong>Fuente actual</strong><small>{translation.source_hash.slice(0, 16)}</small></div><button className="button button-light" onClick={() => void exportArtifact("source")}>Descargar .psc ↓</button></div>
            <MappedCode code={source} mappings={[]} onSelect={() => { setTab("editor"); }} />
            <div className="code-pane-foot"><span>Span original · línea y columna</span><button className="text-button" onClick={() => { setTab("editor"); setSelectedInspector("tokens"); }}>Editar fuente ↗</button></div>
          </article>
          {(["python", "javascript"] as const).map((target) => <article className="panel code-pane" key={target}>
            <div className="code-pane-head"><div><span className="runtime-icon">{target === "python" ? "Py" : "JS"}</span><strong>{target === "python" ? "Python 3" : "JavaScript · Node.js"}</strong><small>{translation.artifacts[target].artifact_hash.slice(0, 16)}</small></div><div><button className="icon-button" aria-label={`Copiar código ${target}`} onClick={async () => { await navigator.clipboard.writeText(translation.artifacts[target].source); setNotice(`Código ${target} copiado.`); }}>▣</button><button className="button button-light" onClick={() => void exportArtifact(target, source)}>Descargar .{target === "python" ? "py" : "js"} ↓</button></div></div>
            <MappedCode code={translation.artifacts[target].source} mappings={translation.artifacts[target].source_map ?? []} onSelect={focusSpan} />
            <div className="code-pane-foot"><span>Artefacto autónomo · hash verificado</span><span>{translation.artifacts[target].source_map?.length ?? 0} líneas mapeadas</span></div>
          </article>)}
        </div>}
        {translation && <div className="source-map-card"><strong>Mapas de origen</strong><span>Selecciona un token o diagnóstico del inspector para enfocar su span en el editor. El generador adjunta mapa por destino.</span><button onClick={() => { setTab("editor"); setSelectedInspector("phases"); }}>Ver hashes y fases →</button></div>}
      </section>}

      {tab === "console" && <section className="subpage console-page">
        <div className="section-heading"><div><div className="eyebrow">EJECUCIÓN REAL · CONTENEDOR EFÍMERO</div><h1>Consola de ejecución.</h1><p>Entradas y salida de procesos Python o Node aislados con stdin/stdout/stderr reales.</p></div><div className="run-status"><i className={busy.startsWith("run-") || busy.startsWith("interactive-") ? "working" : sandboxStatus ? "ready" : "offline"} />{busy.startsWith("run-") || busy.startsWith("interactive-") ? "Ejecutando" : sandboxStatus ? "Sandbox listo" : "No disponible"}</div></div>
        <div className="console-controls panel"><div className="input-field"><label htmlFor="batch-inputs">Entradas por lote · un valor por línea</label><textarea id="batch-inputs" value={batchInputs} onChange={(event) => setBatchInputs(event.target.value)} placeholder="Ej. 41" rows={3} /></div><div className="console-actions"><button className="button button-dark" onClick={() => void runBatch("python")} disabled={!sandboxStatus || Boolean(busy) || currentCompileInvalid}>▶ Python lote</button><button className="button button-dark" onClick={() => void runBatch("javascript")} disabled={!sandboxStatus || Boolean(busy) || currentCompileInvalid}>▶ JavaScript lote</button><button className="button button-light" onClick={() => startInteractive("python")} disabled={!sandboxStatus || Boolean(busy) || currentCompileInvalid}>◉ Python interactivo</button><button className="button button-light" onClick={() => startInteractive("javascript")} disabled={!sandboxStatus || Boolean(busy) || currentCompileInvalid}>◉ JS interactivo</button>{(Boolean(activeRunId) || Boolean(wsRef.current) || busy.startsWith("run-") || busy.startsWith("interactive-")) && <button className="button button-danger" onClick={() => void cancelRun()}>■ Detener</button>}</div></div>
        <div className="terminal panel"><div className="terminal-head"><div><i /><i /><i /></div><span>{busy ? "PROCESO ACTIVO" : "SALIDA DEL RUNTIME"}</span><button className="text-button" onClick={() => setConsoleText("")}>Limpiar</button></div><pre className="terminal-output" aria-live="polite">{consoleText || <span className="terminal-placeholder">La salida real aparecerá aquí al ejecutar el programa.</span>}</pre>{inputRequested && <form className="terminal-input" onSubmit={sendInteractiveInput}><label htmlFor="interactive-value">El programa solicita entrada</label><input id="interactive-value" autoFocus value={interactiveInput} onChange={(event) => setInteractiveInput(event.target.value)} /><button className="button button-accent" type="submit">Enviar ↵</button></form>}</div>
        <section className="run-history"><div className="list-heading"><div><div className="eyebrow">TRAZABILIDAD</div><h2>Sesiones recientes</h2></div><span>Los valores de entrada no se guardan en el historial.</span></div>{runs.length ? <div className="run-table"><div className="run-table-head"><span>Destino</span><span>Estado</span><span>Exit</span><span>Duración</span><span>Versión</span><span>Hash de fuente</span></div>{runs.map((run) => <div className="run-table-row" key={run.run_id}><span>{run.target}</span><span className={run.status === "completed" ? "text-good" : "text-bad"}>{run.status}</span><span>{run.exit_code ?? "—"}</span><span>{Number(run.duration_ms).toFixed(1)} ms</span><span>{run.runtime_version}</span><code>{run.source_hash.slice(0, 12)}</code></div>)}</div> : <p className="muted">Aún no hay ejecuciones en esta sesión.</p>}</section>
      </section>}

      {tab === "tests" && <section className="subpage">
        <div className="section-heading"><div><div className="eyebrow">PYTHON + NODE.JS · COMPARACIÓN EXACTA</div><h1>Pruebas académicas y propias.</h1><p>Cada prueba ejecuta el mismo programa en los dos runtimes y compara stdout completo.</p></div><div className="heading-actions"><button className="button button-light" onClick={() => report && void exportArtifact("report-json", source, report.report_id)} disabled={!report}>JSON ↓</button><button className="button button-light" onClick={() => report && void exportArtifact("report-markdown", source, report.report_id)} disabled={!report}>Markdown ↓</button><button className="button button-accent" onClick={() => report && void exportArtifact("report-pdf", source, report.report_id)} disabled={!report}>PDF ↓</button></div></div>
        <div className="test-layout"><div className="panel test-card"><div className="eyebrow">BIBLIOTECA OFICIAL</div><h2>Casos A–E</h2><p>Casos y salidas oficiales cargados desde fixtures reproducibles.</p><label htmlFor="official-example">Programa</label><select id="official-example" value={exampleId} onChange={(event) => setExampleId(event.target.value)}>{examples.map((item) => <option key={item.id} value={item.id}>{item.id} · {exampleTitles[item.id]}</option>)}</select><button className="button button-dark full-button" onClick={() => void runTests(true)} disabled={!sandboxStatus || Boolean(busy)}>{busy === "tests" ? "Ejecutando…" : `Ejecutar ${exampleId} en ambos destinos`}</button><small>6 ejecuciones OCI reales · 3 casos × Python y Node.js</small></div>
          <div className="panel test-card"><div className="eyebrow">MATRIZ EDITABLE</div><div className="list-heading"><h2>Casos propios</h2><button className="text-button" onClick={() => setTestCases((current) => [...current, { id: `propio-${current.length + 1}`, inputs: "", expected_stdout: "" }])}>＋ Añadir caso</button></div><p>Las entradas se suministran por línea; la salida esperada se compara literalmente.</p>{testCases.map((item, index) => <div className="editable-case" key={`${index}-${item.id}`}><div className="editable-case-heading"><label htmlFor={`case-id-${index}`}>Caso {index + 1}<input id={`case-id-${index}`} value={item.id} onChange={(event) => setTestCases((current) => current.map((caseItem, caseIndex) => caseIndex === index ? { ...caseItem, id: event.target.value } : caseItem))} /></label>{testCases.length > 1 && <button className="text-button remove-case" onClick={() => setTestCases((current) => current.filter((_, caseIndex) => caseIndex !== index))}>Eliminar</button>}</div><label htmlFor={`case-inputs-${index}`}>Entradas</label><textarea id={`case-inputs-${index}`} aria-label={`Entradas del caso ${index + 1}`} rows={2} value={item.inputs} onChange={(event) => setTestCases((current) => current.map((caseItem, caseIndex) => caseIndex === index ? { ...caseItem, inputs: event.target.value } : caseItem))} /><label htmlFor={`case-expected-${index}`}>stdout esperado, incluye saltos de línea</label><textarea id={`case-expected-${index}`} aria-label={`stdout esperado del caso ${index + 1}`} rows={3} value={item.expected_stdout} onChange={(event) => setTestCases((current) => current.map((caseItem, caseIndex) => caseIndex === index ? { ...caseItem, expected_stdout: event.target.value } : caseItem))} /></div>)}<button className="button button-accent full-button" onClick={() => void runTests(false)} disabled={!sandboxStatus || Boolean(busy) || currentCompileInvalid}>Ejecutar casos propios en Python + JS</button></div></div>
        {report && <div className="report-result"><div className="report-summary"><div className={`result-mark ${report.failed ? "failed" : "passed"}`}>{report.failed ? "!" : "✓"}</div><div><div className="eyebrow">INFORME · {report.source_hash?.slice(0, 12)}</div><h2>{report.passed} / {report.total} ejecuciones aprobadas</h2><p>{report.failed ? `${report.failed} diferencias detectadas.` : "Las salidas coinciden con los resultados esperados."}</p></div><button className="text-button" onClick={() => downloadText("pseudo-studio-report.json", JSON.stringify(report, null, 2), "application/json")}>Guardar JSON local ↓</button></div>
          {report.comparisons?.length > 0 && <section className="target-comparisons" aria-label="Comparación Python y JavaScript"><h3>Comparación Python ↔ Node</h3>{report.comparisons.map((item: any) => <div className="target-comparison" key={item.case_id}><strong>{item.case_id}</strong><span className={item.equivalent ? "text-good" : "text-bad"}>{item.equivalent ? "Equivalentes" : item.reason === "MISSING_TARGET" ? "Falta un destino" : "Difieren"}</span><small>stdout {item.raw_stdout_match ? "idéntico" : item.normalized_stdout_match ? "solo cambia el fin de línea" : "distinto"} · stderr {item.raw_stderr_match ? "idéntico" : item.normalized_stderr_match ? "solo cambia el fin de línea" : "distinto"}</small>{item.stdout_diff && <pre>{item.stdout_diff}</pre>}{item.stderr_diff && <pre>{item.stderr_diff}</pre>}</div>)}</section>}
          <div className="case-results">{report.runs?.map((item: any, index: number) => <details className="case-result" key={`${item.case_id}-${item.target}-${index}`}><summary><span className={`result-dot ${item.passed ? "passed" : "failed"}`} /><strong>{item.case_id}</strong><span>{item.target}</span><span className={item.passed ? "text-good" : "text-bad"}>{item.passed ? "Aprobado" : "Falló"}</span><small>{Number(item.duration_ms).toFixed(1)} ms · exit {item.exit_code}</small></summary><div className="result-diff"><div><strong>Esperado</strong><pre>{item.expected_stdout}</pre></div><div><strong>Real</strong><pre>{item.actual_stdout}</pre></div>{item.stderr && <div><strong>stderr · {item.error_code}</strong><pre>{item.stderr}</pre></div>}{item.diff && <pre>{item.diff}</pre>}<code>artifact SHA-256 {item.artifact_hash}</code></div></details>)}</div></div>}
      </section>}

      {tab === "projects" && <section className="subpage">
        <div className="section-heading"><div><div className="eyebrow">PERSISTENCIA SQLITE LOCAL</div><h1>Tus proyectos.</h1><p>Los proyectos se guardan en la base local del backend. Los valores usados al ejecutar se excluyen del historial.</p></div><div className="heading-actions"><button className="button button-light" onClick={() => void refreshProjects()}>↻ Actualizar</button><button className="button button-accent" onClick={() => void saveNewProject()}>＋ Guardar fuente actual</button></div></div>
        <div className="projects-layout"><div className="project-list panel"><div className="list-heading"><h2>Proyectos guardados</h2><span>{projects.length} elementos</span></div>{projects.map((item) => <article className={`project-row ${project?.id === item.id ? "current" : ""}`} key={item.id}><button className="project-open" onClick={() => void openProject(item.id)}><span className="project-file">.psc</span><span><strong>{item.name}</strong><small>Actualizado {new Date(item.updated_at).toLocaleString("es")}</small></span></button><button className="icon-button" title="Duplicar" aria-label={`Duplicar ${item.name}`} onClick={() => void duplicateProjectById(item.id)}>⧉</button><button className="icon-button danger-quiet" title="Eliminar" aria-label={`Eliminar ${item.name}`} onClick={() => void deleteProject(item)}>×</button></article>)}{!projects.length && <div className="empty-state compact"><strong>No hay proyectos guardados</strong><p>Guarda el borrador actual para conservarlo localmente.</p></div>}</div>
          <div className="project-detail panel"><div className="eyebrow">PROYECTO ACTUAL</div>{project ? <><input className="project-name-input" aria-label="Nombre del proyecto" value={projectName} onChange={(event) => { setProjectName(event.target.value); setProjectState("Cambios pendientes"); }} /><p>Versión {project.version} · {project.source_hash.slice(0, 16)}</p><div className="project-actions"><button className="button button-dark" onClick={() => void saveProject()}>Guardar ahora</button><button className="button button-light" onClick={() => void duplicateProject()}>Duplicar</button><button className="button button-quiet" onClick={() => void deleteProject(project)}>Eliminar</button></div><div className="project-save-state"><i className={projectState.includes("Guardado") ? "good" : "pending"} />{projectState}</div><h3>Historial de ejecuciones</h3><p>{runs.length} ejecuciones cargadas para este proyecto. Consulta la consola para ver destinos, exit code, duración y hashes.</p></> : <><h2>Borrador actual</h2><p>{projectState}. Este texto se conserva en el almacenamiento local del navegador y puede guardarse en SQLite.</p><button className="button button-accent" onClick={() => void saveNewProject()}>Crear proyecto</button></>}</div></div>
      </section>}

      {tab === "defense" && <section className="subpage">
        <div className="section-heading"><div><div className="eyebrow">RECORRIDO GUIADO · PIPELINE REAL</div><h1>Modo defensa.</h1><p>Avanza por las fases del compilador, inspecciona evidencia y prueba una entrada válida o una fuente con error.</p></div><div className="heading-actions"><button className="button button-light" onClick={() => { setDefenseLog([]); setDefenseStep(-1); }}>Reiniciar recorrido</button><button className="button button-accent" onClick={() => void runDefenseStep()} disabled={Boolean(busy)}>Siguiente fase →</button></div></div>
        <div className="defense-layout"><div className="panel defense-setup"><div className="eyebrow">FUENTE DE DEMOSTRACIÓN</div><div className="segmented"><button className={defenseCase === "valid" ? "active" : ""} onClick={() => { setDefenseCase("valid"); setDefenseStep(-1); setDefenseLog([]); void loadExample("A"); }}>Caso válido · A</button><button className={defenseCase === "invalid" ? "active" : ""} onClick={() => { setDefenseCase("invalid"); setDefenseStep(-1); setDefenseLog([]); setSourceChanged(INVALID_SAMPLE); setProject(null); setProjectName("Caso de error léxico"); setAnalysis(null); setTranslation(null); setNotice("Fuente de ejemplo con error léxico. El servicio calculará su diagnóstico al avanzar."); }}>Caso con error</button></div><p>El recorrido usará la fuente del editor y solicitará cada fase a la API real. Estado actual: {defenseStep < 0 ? "pendiente" : `fase ${defenseStep + 1} de 5`}.</p><button className="button button-light" onClick={() => setTab("editor")}>Abrir fuente en editor ↗</button></div>
          <div className="panel defense-log"><div className="list-heading"><div><div className="eyebrow">BITÁCORA</div><h2>Evidencia calculada</h2></div><button className="text-button" onClick={() => downloadText("pseudo-studio-defense.json", JSON.stringify(defenseLog, null, 2), "application/json")}>Exportar ↓</button></div>{defenseLog.length ? defenseLog.map((item, index) => <article className="defense-entry" key={`${item.phase}-${index}`}><span>{String(index + 1).padStart(2, "0")}</span><div><strong>{item.phase}</strong><p>{item.result}</p>{item.source_hash && <code>SHA {item.source_hash}</code>}</div><small>calculado</small></article>) : <div className="empty-state compact"><strong>Sin fases ejecutadas</strong><p>Pulsa “Siguiente fase” para comenzar el recorrido.</p></div>}</div></div>
      </section>}

      {tab === "help" && <section className="subpage help-page">
        <div className="section-heading"><div><div className="eyebrow">MANUAL DEL LENGUAJE</div><h1>Reglas claras, ejecución reproducible.</h1><p>Gramática cargada desde el documento EBNF del repositorio.</p></div><button className="button button-light" onClick={() => downloadText("gramatica-pseudocodigo.ebnf", grammar, "text/plain;charset=utf-8")}>Descargar EBNF ↓</button></div>
        <div className="help-grid"><article className="panel help-card"><div className="eyebrow">ESTRUCTURA</div><h2>Un programa</h2><pre>{`Inicio
  Leer numero
  Escribir "Doble: ", numero * 2
Fin`}</pre><p>Una sentencia termina al final de línea. Los bloques usan terminadores explícitos y la indentación es opcional.</p></article><article className="panel help-card"><div className="eyebrow">CONTROL Y DATOS</div><h2>Construcciones</h2><ul><li><code>Si / Entonces / Sino / FinSi</code></li><li><code>Para / Hasta / Paso / Hacer / FinPara</code></li><li><code>Mientras / Hacer / FinMientras</code></li><li><code>Dimension a[n]</code> con índices desde 1</li><li><code>Funcion f(x) … Retornar … FinFuncion</code></li><li><code>Y, O, No</code> con cortocircuito</li></ul></article><article className="panel help-card grammar-card"><div className="eyebrow">EBNF NORMATIVO</div><h2>Gramática instalada</h2><pre tabIndex={0} aria-label="Gramática EBNF, región desplazable">{grammar || "Cargando docs/gramatica.ebnf desde el servidor…"}</pre></article></div>
      </section>}
    </main>
    <footer className="app-footer"><span>Pseudo / Studio <span>·</span> ejecución local</span><span>API v1 · {health?.components?.compiler?.version ?? "compilador"}</span><span>{projectState}</span></footer>
  </div>;
}

function AstNode({ node, onSelect, depth }: { node: any; onSelect: (span?: Span) => void; depth: number }) {
  if (!node || typeof node !== "object") return <span className="muted">AST no disponible.</span>;
  const children = Object.entries(node).filter(([key, value]) => key !== "span" && (Array.isArray(value) ? value.some((item) => item && typeof item === "object" && "kind" in item) : value && typeof value === "object" && "kind" in (value as object)));
  return <details className="ast-node" open={depth < 2} style={{ marginLeft: `${depth * 10}px` }}><summary onClick={() => onSelect(node.span)}><span className="ast-kind">{node.kind}</span><code>{node.node_id}</code><small>{node.span?.start_line}:{node.span?.start_column}</small></summary><div>{children.map(([key, value]) => Array.isArray(value)
    ? value.filter((item) => item && typeof item === "object" && "kind" in item).map((item, index) => <AstNode key={`${key}-${index}`} node={item} onSelect={onSelect} depth={depth + 1} />)
    : <AstNode key={key} node={value} onSelect={onSelect} depth={depth + 1} />)}</div></details>;
}

function MappedCode({ code, mappings, onSelect }: {
  code: string;
  mappings: Array<{ generated_line: number; source_span: Span }>;
  onSelect: (span?: Span) => void;
}) {
  const byLine = new Map(mappings.map((mapping) => [mapping.generated_line, mapping.source_span]));
  return <pre className="generated-code mapped-code"><code>{code.split("\n").map((line, index) => {
    const generatedLine = index + 1;
    const span = byLine.get(generatedLine);
    return <button type="button" className={`mapped-line ${span ? "mapped" : ""}`} key={generatedLine} disabled={!span} title={span ? `Fuente: línea ${span.start_line}, columna ${span.start_column}` : undefined} onClick={() => onSelect(span)}>
      <span className="generated-line-number">{generatedLine}</span><span className="generated-line-text">{line || " "}</span>
    </button>;
  })}</code></pre>;
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
