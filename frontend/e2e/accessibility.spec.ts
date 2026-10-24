import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("workbench editor meets automated WCAG 2.2 A/AA checks", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("API lista")).toBeVisible();
  const violations = [];
  for (const tab of ["Editor", "Traducción", "Equivalencias", "Consola", "Pruebas", "Proyectos", "Defensa", "Ayuda"]) {
    await page.getByRole("button", { name: tab, exact: true }).click();
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"])
      .analyze();
    violations.push(...results.violations.map((violation) => ({
      tab,
      id: violation.id,
      nodes: violation.nodes.map((node) => ({ target: node.target, html: node.html, contrast: node.any[0]?.data })),
    })));
  }
  await page.getByRole("button", { name: "Editor", exact: true }).focus();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Traducción", exact: true })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("heading", { name: "Dos destinos, una fuente." })).toBeVisible();
  expect(violations, JSON.stringify(violations, null, 2)).toEqual([]);
});

test("every workspace section can be reached and activated by keyboard", async ({ page }) => {
  await page.goto("/");
  const sections = [
    ["Traducción", "Dos destinos, una fuente."],
    ["Equivalencias", "Un lenguaje, dos traducciones."],
    ["Consola", "Consola de ejecución."],
    ["Pruebas", "Pruebas académicas y propias."],
    ["Proyectos", "Tus proyectos."],
    ["Defensa", "Modo defensa."],
    ["Ayuda", "Reglas claras, ejecución reproducible."],
  ] as const;

  await page.getByRole("button", { name: "Editor", exact: true }).focus();
  await expect(page.getByRole("heading", { name: "Escribe en pseudocódigo." })).toBeVisible();
  for (const [section, heading] of sections) {
    await page.keyboard.press("Tab");
    const navigationButton = page.getByRole("button", { name: section, exact: true });
    await expect(navigationButton).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(navigationButton).toHaveAttribute("aria-current", "page");
    await expect(page.getByRole("heading", { name: heading, exact: true })).toBeVisible();
  }
});
