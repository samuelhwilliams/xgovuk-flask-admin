/**
 * Auto-submit Component
 *
 * Automatically submits a form when a select element changes.
 * This removes the need for inline onchange attributes, making it CSP-compliant.
 *
 * Usage:
 * Add data-module="auto-submit" to a select element within a form.
 * The form will be submitted automatically when the selection changes.
 *
 * Example:
 * <form id="my-form">
 *   <select data-module="auto-submit" name="page_size">
 *     <option value="20">20 per page</option>
 *     <option value="50">50 per page</option>
 *   </select>
 * </form>
 */

// Ensure GOVUK namespace exists
window.GOVUK = window.GOVUK || {};
window.GOVUK.Modules = window.GOVUK.Modules || {};

(function (Modules) {
    function AutoSubmit(module) {
        this.module = module;
    }

    AutoSubmit.prototype.init = function () {
        if (!this.module.matches("select")) {
            console.error(
                "AutoSubmit module must be applied to a select element",
            );
            return;
        }

        const form = this.module.closest("form");
        if (!form) {
            console.error(
                "AutoSubmit module requires select to be within a form",
            );
            return;
        }

        this.module.addEventListener("change", function () {
            form.submit();
        });
    };

    Modules.AutoSubmit = AutoSubmit;
})(window.GOVUK.Modules);

export default window.GOVUK.Modules.AutoSubmit;
