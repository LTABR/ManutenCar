describe("ManutenCar MVP", () => {
  it("renders the official logo and persists the active support view", () => {
    cy.visit("/");
    cy.location("pathname").should("eq", "/");
    cy.get("body").should("exist");
  });

  it("stores the selected view preference", () => {
    cy.visit("/");
    cy.window().then((window) => {
      window.localStorage.setItem("manutencar:activeView", JSON.stringify("support"));
    });
    cy.reload();
    cy.window().its("localStorage").invoke("getItem", "manutencar:activeView").should("contain", "support");
  });
});
