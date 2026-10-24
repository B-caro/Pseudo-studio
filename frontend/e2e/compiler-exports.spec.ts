import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

test("editor highlights the language's modulo keyword", async ({ page }) => {
  await page.goto("/");
  const editor = page.locator(".cm-content");
  await editor.fill("Inicio\nresultado = 5 Modulo 2\nFin\n");
  await expect(editor.locator("span").filter({ hasText: "Modulo" }).first()).toHaveCSS("color", "rgb(180, 76, 55)");
});

test("startup waits for the initial example before allowing compilation", async ({ page }) => {
  await page.addInitScript(() => localStorage.clear());
  await page.route("**/api/v1/examples/A", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1200));
    await route.continue();
  });
  await page.goto("/");
  const analyze = page.getByRole("button", { name: "◎ Analizar" });
  await expect(analyze).toBeDisabled();
  await expect(page.locator(".cm-content")).toContainText("Leer numero");
  await expect(analyze).toBeEnabled();
  await expect(page.locator(".cm-content")).toContainText("Ingrese el primer número:");
  await analyze.click();
  await expect(page.getByText("46 tokens", { exact: true })).toBeVisible();
});

test("API and UI analyze real source and export equivalent code and actionable errors as TXT", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator(".status-pill")).toContainText(/lista|degraded/);

  const source = 'Inicio\nLeer cantidad\nEscribir "Total=", cantidad * 2\nFin\n';
  await page.locator(".cm-content").fill(source);
  await page.getByRole("button", { name: "◎ Analizar" }).click();
  await expect(page.getByText(/tokens ·/)).toBeVisible();
  await page.getByRole("tab", { name: "AST" }).click();
  await expect(page.getByText("Write", { exact: true })).toBeVisible();
  const binaryNode = page.locator(".ast-node").filter({ has: page.getByText("Binary", { exact: true }) }).last();
  await binaryNode.locator(":scope > summary").click();
  await expect(binaryNode.getByText("operator: *", { exact: true })).toBeVisible();
  await expect(binaryNode.getByText("izquierda", { exact: true })).toBeVisible();

  await page.getByRole("button", { name: "Traducción" }).click();
  await page.getByRole("button", { name: "Traducir fuente actual" }).click();
  await expect(page.getByText("JavaScript · Node.js", { exact: true })).toBeVisible();

  const pythonFilePromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar .py" }).click();
  const pythonFile = await pythonFilePromise;
  const pythonBytes = await readFile((await pythonFile.path())!);
  const pythonTextPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar Python .txt ↓" }).click();
  const pythonText = await pythonTextPromise;
  expect(await readFile((await pythonText.path())!)).toEqual(pythonBytes);

  const javascriptFilePromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar .js" }).click();
  const javascriptFile = await javascriptFilePromise;
  const javascriptBytes = await readFile((await javascriptFile.path())!);
  const javascriptTextPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Descargar JavaScript .txt ↓" }).click();
  const javascriptText = await javascriptTextPromise;
  expect(await readFile((await javascriptText.path())!)).toEqual(javascriptBytes);

  await page.getByRole("button", { name: "Editor" }).click();
  await page.locator(".cm-content").fill("Inicio\nEscribir @\nFin\n");
  await page.getByRole("button", { name: "◎ Analizar" }).click();
  await expect(page.getByRole("tab", { name: /Errores/ })).toBeVisible();
  await expect(page.getByRole("button", { name: "LEX_INVALID_CHAR · lexical" })).toBeVisible();
  const errorsDownloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Exportar errores .txt" }).click();
  const errorsDownload = await errorsDownloadPromise;
  const errors = await readFile((await errorsDownload.path())!, "utf8");
  expect(errors).toContain("SHA-256 de la fuente:");
  expect(errors).toContain("LEX_INVALID_CHAR");
  expect(errors).toContain("Ubicación: línea 2, columna 10");
  expect(errors).toContain("Sugerencia:");

  await page.locator(".cm-content").fill('Inicio\nEscribir "😀"\nEscribir falta\nFin\n');
  await page.getByRole("button", { name: "◎ Analizar" }).click();
  await page.locator(".diagnostic-card").first().click();
  await expect.poll(() => page.evaluate(() => window.getSelection()?.toString() ?? "")).toBe("falta");

  await page.locator(".cm-content").fill("Inicio\nEscribir @\nFin\n");
  await page.getByRole("button", { name: "◎ Analizar" }).click();
  await expect(page.getByRole("button", { name: "Traducir ↗" })).toBeDisabled();
  await page.locator(".cm-content").fill('Inicio\nEscribir "corregido"\nFin\n');
  await page.getByRole("button", { name: "◎ Analizar" }).click();
  await expect(page.getByText(/tokens ·/)).toBeVisible();
  await page.getByRole("button", { name: "Traducir ↗" }).click();
  await expect(page.getByText("Python 3", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Editor" }).click();

  const input = page.locator('input[type="file"]');
  await input.setInputFiles({
    name: "entrada.txt",
    mimeType: "text/plain",
    buffer: Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), Buffer.from('Inicio\r\nEscribir "válido"\r\nFin\r\n')]),
  });
  await expect(page.locator(".cm-content")).toContainText("válido");
  await page.getByRole("button", { name: "◎ Analizar" }).click();
  await expect(page.getByText(/tokens ·/)).toBeVisible();
  for (const name of ["A", "B", "C", "D", "E"]) {
    const original = await readFile(resolve(process.cwd(), `../examples/${name}.psc`), "utf8");
    const windowsText = original.replace(/\n/g, "\r\n");
    await input.setInputFiles({
      name: `${name}.txt`,
      mimeType: "text/plain",
      buffer: Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), Buffer.from(windowsText)]),
    });
    await page.getByRole("button", { name: "◎ Analizar" }).click();
    await expect(page.getByText(/tokens ·/)).toBeVisible();
  }
});
