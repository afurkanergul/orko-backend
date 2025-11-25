describe("ORKO — Smoke Test", () => {
  it("Loads the landing page", () => {
    cy.visit("/");
    cy.contains("ORKO is alive");
  });
});
