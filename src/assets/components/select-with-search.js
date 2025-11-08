/**
 * Select with Search Component
 *
 * Based on govuk_publishing_components select-with-search component
 * Source: https://github.com/alphagov/govuk_publishing_components/blob/6e58485f5219508e4f0fc7db465bdadb58a45d29/app/assets/javascripts/govuk_publishing_components/components/select-with-search.js
 *
 * Uses Choices.js for the enhanced select functionality
 * Choices.js: https://github.com/Choices-js/Choices
 *
 * Changes from original:
 * - Changed from Sprockets (//= require) to ES6 import for Choices.js
 * - Changed `new window.Choices` to `new Choices` (using imported module)
 * - Removed incomplete comment in fuseOptions (original: "threshold: 0 // only matches")
 */
import Choices from "choices.js";

// Ensure GOVUK namespace exists
window.GOVUK = window.GOVUK || {};
window.GOVUK.Modules = window.GOVUK.Modules || {};
(function (Modules) {
    function SelectWithSearch(module) {
        this.module = module;
    }

    SelectWithSearch.prototype.init = function () {
        if (!this.module.matches("select")) {
            console.error("Module is not a select element");
            return;
        }

        const placeholderOption = this.module.querySelector(
            'option[value=""]:first-child',
        );

        if (placeholderOption && placeholderOption.textContent === "") {
            placeholderOption.textContent = this.module.multiple
                ? "Select all that apply"
                : "Select one";
        }

        const ariaDescribedBy =
            this.module.getAttribute("aria-describedby") || "";
        const labelId = this.module.id + "-label " + ariaDescribedBy;

        // Check if duplicate prevention is requested
        const removeDuplicates =
            this.module.getAttribute("data-remove-duplicates") === "true";

        this.choices = new Choices(this.module, {
            allowHTML: false,
            searchPlaceholderValue: "Search in list",
            shouldSort: false, // show options and groups in the order they were given
            itemSelectText: "",
            searchResultLimit: 100,
            removeItemButton: this.module.multiple,
            duplicateItemsAllowed: !removeDuplicates, // Prevent duplicates if requested
            labelId: labelId,
            callbackOnInit: function () {
                // For the multiple select, move the input field to
                // the top of the feedback area, so that the selected
                // 'lozenges' appear afterwards in a more natural flow
                if (this.dropdown.type === "select-multiple") {
                    const inner = this.containerInner.element;
                    const input = this.input.element;
                    inner.prepend(input);
                }
                // Add aria-labelledby to the listbox as well as the combobox
                const listbox = this.itemList.element;
                listbox.setAttribute("aria-labelledby", labelId);
            },
            // https://fusejs.io/api/options.html
            fuseOptions: {
                ignoreLocation: true, // matches any part of the string
                threshold: 0, // only matches when characters are sequential
            },
        });

        this.module.choices = this.choices;
    };

    Modules.SelectWithSearch = SelectWithSearch;
})(window.GOVUK.Modules);

export default window.GOVUK.Modules.SelectWithSearch;
