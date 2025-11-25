describe("ORKO Dashboard Smoke Test", () => {
  it("loads dashboard UI", () => {
    cy.visit("/dashboard");
    cy.contains("Overview", { timeout: 8000 }).should("exist");
  });

  it("renders KPI cards", () => {
    cy.get(".kpi-card").should("have.length", 3);
  });

  it("renders timeline", () => {
    cy.contains("Insights Timeline").should("exist");
  });

  it("opens and closes event modal", () => {
    cy.contains("View").first().click();
    cy.contains("Event Details").should("exist");
    cy.contains("×").click(); // modal close button
  });
});
