import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test("workbench editor meets automated WCAG 2.2 A/AA checks", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("API lista")).toBeVisible();
  const violations = [];
  for (const tab of ["Editor", "Traducción", "Consola", "Pruebas", "Proyectos", "Defensa", "Ayuda"]) {
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
