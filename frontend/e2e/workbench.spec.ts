import { expect, test } from "@playwright/test";
import { resolve } from "node:path";

const sourceWithInput = `Inicio
Leer n
Escribir "U=", n + 1
Fin
`;

async function replaceSource(page: import("@playwright/test").Page, source: string) {
  const editor = page.locator(".cm-content");
  await editor.fill(source);
  await expect(editor).toContainText("Inicio");
}

test("analyze and translate real source, show diagnostics and provide working downloads", async ({ page, context }) => {
  await page.goto("/");
  await expect(page.getByText("API lista")).toBeVisible();
  await expect(page.getByText("Sandbox verificado")).toBeVisible();
  await page.getByRole("button", { name: "Actualizar estado" }).click();
  await page.getByRole("button", { name: "◎ Analizar" }).click();
  await expect(page.getByText(/tokens ·/)).toBeVisible();
  await page.getByRole("button", { name: "Inicio KEYWORD 1:1" }).click();
  await expect(page.locator(".cm-content")).toBeFocused();
  await page.getByRole("tab", { name: "AST" }).click();
  await expect(page.getByText("Program", { exact: true })).toBeVisible();
  await page.locator(".ast-node > summary").first().click();
  await expect(page.locator(".cm-content")).toBeFocused();
  await page.screenshot({ path: resolve(process.cwd(), "../reports/ui-workbench.png"), fullPage: true });
  await page.getByRole("button", { name: "Traducción" }).click();
  await page.getByRole("button", { name: "Traducir fuente actual" }).click();
  await expect(page.getByText("Python 3", { exact: true })).toBeVisible();
  await expect(page.getByText("JavaScript · Node.js", { exact: true })).toBeVisible();
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.getByRole("button", { name: "Copiar código python" }).click();
  await expect(page.getByRole("status")).toContainText("Código python copiado");
  expect(await page.evaluate(() => navigator.clipboard.readText())).toContain("__ps_write");
  await page.locator(".mapped-line.mapped").first().click();
  await expect(page.getByRole("button", { name: "Editor" })).toHaveClass(/active/);
  await page.getByRole("button", { name: "Traducción" }).click();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar .py" }).click();
  expect((await downloadPromise).suggestedFilename()).toContain("pseudo-studio-python-");
  const jsDownloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar .js" }).click();
  expect((await jsDownloadPromise).suggestedFilename()).toContain("pseudo-studio-javascript-");
  const sourceDownloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar .psc ↓" }).first().click();
  expect((await sourceDownloadPromise).suggestedFilename()).toContain("pseudo-studio-source-");

  await page.getByRole("button", { name: "Editor" }).click();
  for (const [tab, filename] of [["Tokens", "tokens"], ["Símbolos", "symbols"], ["Fases", "phases"]] as const) {
    await page.getByRole("tab", { name: tab }).click();
    const exportPromise = page.waitForEvent("download");
    await page.getByRole("button", { name: "Exportar JSON ↓" }).click();
    expect((await exportPromise).suggestedFilename()).toContain(filename);
  }
  await replaceSource(page, "Inicio\nEscribir @\nFin\n");
  await page.getByRole("button", { name: "◎ Analizar" }).click();
  await page.getByRole("tab", { name: /Errores/ }).click();
  await expect(page.getByText("LEX_INVALID_CHAR", { exact: false })).toBeVisible();
  await page.locator(".diagnostic-card").first().click();
  await expect(page.locator(".cm-content")).toBeFocused();
  await expect(page.getByRole("button", { name: "Traducir ↗" })).toBeDisabled();
  const diagnosticsDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Exportar JSON ↓" }).click();
  expect((await diagnosticsDownload).suggestedFilename()).toContain("diagnostics");
  await page.getByRole("button", { name: "Cerrar aviso" }).click();
  await expect(page.getByRole("status")).toHaveCount(0);
  await page.locator('input[type="file"]').setInputFiles({
    name: "cargado.psc", mimeType: "text/plain", buffer: Buffer.from('Inicio\nEscribir "archivo abierto"\nFin\n'),
  });
  await expect(page.locator(".cm-content")).toContainText("archivo abierto");
  await page.getByRole("button", { name: "◎ Analizar" }).click();
  await expect(page.getByText(/tokens ·/)).toBeVisible();
  await page.getByRole("button", { name: /Ejecutar Python/ }).click();
  await expect(page.locator(".terminal-output")).toContainText("archivo abierto");
  await page.getByRole("button", { name: "Editor" }).click();
  await page.getByRole("button", { name: /Ejecutar JavaScript/ }).click();
  await expect(page.locator(".terminal-output")).toContainText("archivo abierto");
  await page.getByRole("button", { name: "Limpiar" }).click();
  await expect(page.locator(".terminal-placeholder")).toContainText("La salida real aparecerá aquí");
});

test("run both targets, stream interactive input, test cases, projects and report exports", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("API lista")).toBeVisible();
  await replaceSource(page, sourceWithInput);
  await page.getByRole("button", { name: "Consola", exact: true }).click();
  await page.getByLabel("Entradas por lote · un valor por línea").fill("41");
  await page.getByRole("button", { name: "Python lote" }).click();
  await expect(page.locator(".terminal-output")).toContainText("U=42");
  await page.getByRole("button", { name: "JavaScript lote" }).click();
  await expect(page.locator(".terminal-output")).toContainText("U=42");
  await page.getByRole("button", { name: "Limpiar" }).click();
  await expect(page.locator(".terminal-placeholder")).toContainText("La salida real aparecerá aquí");

  await page.getByRole("button", { name: "Editor", exact: true }).click();
  await replaceSource(page, `Inicio
Escribir "Numero?"
Leer n
Escribir "R=", n + 1
Fin
`);
  await page.getByRole("button", { name: "Consola", exact: true }).click();
  await page.getByRole("button", { name: "Python interactivo" }).click();
  await expect(page.getByLabel("El programa solicita entrada")).toBeVisible();
  await page.getByLabel("El programa solicita entrada").fill("41");
  await page.getByRole("button", { name: "Enviar" }).click();
  await expect(page.locator(".terminal-output")).toContainText("R=42");
  await expect(page.locator(".terminal-output")).toContainText("completed");
  await page.getByRole("button", { name: "JS interactivo" }).click();
  await expect(page.getByLabel("El programa solicita entrada")).toBeVisible();
  await page.getByLabel("El programa solicita entrada").fill("8");
  await page.getByRole("button", { name: "Enviar" }).click();
  await expect(page.locator(".terminal-output")).toContainText("R=9");
  await expect(page.locator(".terminal-output")).toContainText("completed");

  await page.getByRole("button", { name: "Editor" }).click();
  await replaceSource(page, "Inicio\ni = 0\nMientras Verdadero Hacer\ni = i + 1\nFinMientras\nFin\n");
  await page.getByRole("button", { name: "Consola", exact: true }).click();
  await page.getByRole("button", { name: "Python lote" }).click();
  await page.getByRole("button", { name: /Detener/ }).click();
  await expect(page.locator(".terminal-output")).toContainText("cancelled", { timeout: 15_000 });

  await page.getByRole("button", { name: "Editor" }).click();
  await replaceSource(page, `Inicio
Leer n
Escribir "R=", n + 1
Fin
`);

  await page.getByRole("button", { name: "Pruebas" }).click();
  await page.getByLabel("Entradas del caso 1").fill("41");
  await page.getByLabel("stdout esperado del caso 1").fill("R=42\n");
  await page.getByRole("button", { name: "＋ Añadir caso" }).click();
  await page.getByLabel("Entradas del caso 2").fill("42");
  await page.getByLabel("stdout esperado del caso 2").fill("R=43\n");
  await page.getByRole("button", { name: "Ejecutar casos propios en Python + JS" }).click();
  await expect(page.getByText("4 / 4 ejecuciones aprobadas")).toBeVisible();
  const jsonReportDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "JSON ↓", exact: true }).click();
  expect((await jsonReportDownload).suggestedFilename()).toContain("report-json");
  const markdownDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Markdown ↓", exact: true }).click();
  expect((await markdownDownload).suggestedFilename()).toContain("report-markdown");
  const reportDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "PDF ↓" }).click();
  expect((await reportDownload).suggestedFilename()).toContain("report-pdf");
  const localReportDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Guardar JSON local ↓" }).click();
  expect((await localReportDownload).suggestedFilename()).toContain("pseudo-studio-report.json");
  await page.getByRole("button", { name: "Eliminar", exact: true }).last().click();
  await expect(page.getByLabel("Entradas del caso 2")).toHaveCount(0);

  await page.getByRole("button", { name: "Proyectos" }).click();
  const projectName = `Playwright ${Date.now()}`;
  page.once("dialog", (dialog) => dialog.accept(projectName));
  await page.getByRole("button", { name: "＋ Guardar fuente actual" }).click();
  await expect(page.getByLabel("Nombre del proyecto")).toHaveValue(projectName);
  await page.getByRole("button", { name: "Editor" }).click();
  await replaceSource(page, "Inicio\nEscribir \"persistido\"\nFin\n");
  await page.getByRole("button", { name: "Proyectos" }).click();
  await expect(page.locator(".project-save-state")).toHaveText("Guardado automáticamente", { timeout: 10_000 });
  await page.reload();
  await page.getByRole("button", { name: "Proyectos" }).click();
  await page.getByRole("button", { name: "↻ Actualizar" }).click();
  const savedProject = page.locator(".project-row").filter({ hasText: projectName });
  await expect(savedProject.locator(".project-open")).toBeVisible();
  await savedProject.locator(".project-open").click();
  await expect(page.getByRole("status")).toContainText(/Proyecto abierto · revisión/);
  await page.getByRole("button", { name: "Editor" }).click();
  await expect(page.locator(".cm-content")).toContainText("persistido");
  await page.getByRole("button", { name: "◎ Analizar" }).click();
  await expect(page.getByText(/tokens ·/)).toBeVisible();
  await page.getByRole("button", { name: "Consola", exact: true }).click();
  await page.getByRole("button", { name: "Python lote" }).click();
  await expect(page.locator(".terminal-output")).toContainText("persistido");
  await page.getByRole("button", { name: "JavaScript lote" }).click();
  await expect(page.locator(".terminal-output")).toContainText("persistido");

  await page.getByRole("button", { name: "Proyectos" }).click();
  const renamedProject = `${projectName} Renombrado`;
  await page.getByLabel("Nombre del proyecto").fill(renamedProject);
  await expect(page.locator(".project-save-state")).toHaveText("Guardado automáticamente", { timeout: 10_000 });
  await page.locator(".topbar .header-actions .button-dark").click();
  await expect(page.getByRole("status")).toContainText("Cambios guardados");
  await page.getByRole("button", { name: "Duplicar", exact: true }).click();
  const duplicateName = `${renamedProject} (copia)`;
  await expect(page.getByLabel("Nombre del proyecto")).toHaveValue(duplicateName);
  await expect(page.locator(".project-row").filter({ hasText: duplicateName })).toBeVisible();
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Eliminar", exact: true }).click();
  await expect(page.locator(".project-row").filter({ hasText: duplicateName })).toHaveCount(0);
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByLabel(`Eliminar ${renamedProject}`).click();
  await expect(page.locator(".project-row").filter({ hasText: renamedProject })).toHaveCount(0);
});

test("official test panel runs every official A-E case through Python and Node", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("API lista")).toBeVisible();
  await page.getByRole("button", { name: "Pruebas" }).click();
  for (const program of ["A", "B", "C", "D", "E"]) {
    await page.getByLabel("Programa").selectOption(program);
    const reportResponse = page.waitForResponse((response) =>
      response.url().endsWith("/api/v1/tests/run") && response.request().method() === "POST",
    );
    await page.getByRole("button", { name: `Ejecutar ${program} en ambos destinos` }).click();
    const response = await reportResponse;
    expect(response.ok()).toBeTruthy();
    const report = await response.json();
    expect(report.total).toBe(6);
    expect(report.passed).toBe(6);
    expect(report.runs.map((run: { case_id: string }) => run.case_id)).toEqual(
      [`${program}-1`, `${program}-1`, `${program}-2`, `${program}-2`, `${program}-3`, `${program}-3`],
    );
    expect(report.runs.every((run: { actual_stdout: string; expected_stdout: string; exit_code: number }) =>
      run.actual_stdout === run.expected_stdout && run.exit_code === 0,
    )).toBeTruthy();
    expect(report.comparisons).toHaveLength(3);
    expect(report.comparisons.every((comparison: { equivalent: boolean }) => comparison.equivalent)).toBeTruthy();
    await expect(page.getByText("6 / 6 ejecuciones aprobadas")).toBeVisible({ timeout: 60_000 });
    await expect(page.getByRole("heading", { name: "Comparación Python ↔ Node" })).toBeVisible();
  }
  await expect(page.locator(".case-result summary").getByText("E-1", { exact: true })).toHaveCount(2);
  await expect(page.locator(".case-result summary").getByText("E-3", { exact: true })).toHaveCount(2);
});

test("navigate every workspace section, run defense phases and render on a phone viewport", async ({ page }) => {
  await page.goto("/");
  for (const [tab, heading] of [
    ["Traducción", "Dos destinos, una fuente."],
    ["Consola", "Consola de ejecución."],
    ["Pruebas", "Pruebas académicas y propias."],
    ["Proyectos", "Tus proyectos."],
    ["Defensa", "Modo defensa."],
    ["Ayuda", "Reglas claras, ejecución reproducible."],
    ["Editor", "Escribe en pseudocódigo."],
  ]) {
    await page.getByRole("button", { name: tab, exact: true }).click();
    await expect(page.getByRole("heading", { name: heading, exact: true })).toBeVisible();
  }
  await page.getByRole("button", { name: "Defensa", exact: true }).click();
  await page.getByRole("button", { name: "Caso con error" }).click();
  await page.getByRole("button", { name: "Siguiente fase →" }).click();
  await expect(page.getByText("Léxico", { exact: true })).toBeVisible();
  await expect(page.getByText(/tokens; fase failed/)).toBeVisible();
  await page.getByRole("button", { name: "Caso válido · A" }).click();
  await page.getByRole("button", { name: "Siguiente fase →" }).click();
  await expect(page.getByText(/tokens; fase ok/)).toBeVisible();
  const defenseExport = page.waitForEvent("download");
  await page.getByRole("button", { name: "Exportar ↓" }).click();
  expect((await defenseExport).suggestedFilename()).toContain("pseudo-studio-defense.json");
  await page.getByRole("button", { name: "Abrir fuente en editor ↗" }).click();
  await expect(page.getByRole("heading", { name: "Escribe en pseudocódigo." })).toBeVisible();
  await page.getByRole("button", { name: "Defensa", exact: true }).click();
  await page.getByRole("button", { name: "Reiniciar recorrido" }).click();
  await expect(page.getByText("Sin fases ejecutadas")).toBeVisible();
  await page.getByRole("button", { name: "Ayuda", exact: true }).click();
  await expect(page.getByText("EBNF NORMATIVO", { exact: true })).toBeVisible();
  const grammarDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar EBNF ↓" }).click();
  expect((await grammarDownload).suggestedFilename()).toBe("gramatica-pseudocodigo.ebnf");

  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "Editor", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Escribe en pseudocódigo." })).toBeVisible();
  const dimensions = await page.evaluate(() => ({ width: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth }));
  expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.width + 1);
});
