import { initAll } from "govuk-frontend";
import { initAll as initAllMOJ } from "@ministryofjustice/frontend";
import { FilterToggleButton } from "@ministryofjustice/frontend/moj/components/filter-toggle-button/filter-toggle-button.mjs";
import "./components/select-with-search.js";
import "./components/auto-submit.js";

initAll();
initAllMOJ();

// Initialize GOVUK modules on page load
document.addEventListener("DOMContentLoaded", () => {
    const selectWithSearchModules = document.querySelectorAll(
        '[data-module="select-with-search"]',
    );
    selectWithSearchModules.forEach((module) => {
        new window.GOVUK.Modules.SelectWithSearch(module).init();
    });

    const autoSubmitModules = document.querySelectorAll(
        '[data-module="auto-submit"]',
    );
    autoSubmitModules.forEach((module) => {
        new window.GOVUK.Modules.AutoSubmit(module).init();
    });
});

// Export FilterToggleButton to global scope so templates can use it
window.FilterToggleButton = FilterToggleButton;

// Dispatch event to signal FilterToggleButton is ready
window.dispatchEvent(new Event("FilterToggleButtonReady"));
