SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: check-html
check-html:
	npx prettier --plugin=prettier-plugin-jinja-template --parser=jinja-template --tab-width=2 --html-whitespace-sensitivity css --bracket-same-line=true --print-width=240 --check **/*.html

.PHONY: format-html
format-html:
	npx prettier --plugin=prettier-plugin-jinja-template --parser=jinja-template --tab-width=2 --html-whitespace-sensitivity css --bracket-same-line=true --print-width=240 --write **/*.html

.PHONY: format-css-js
format-css-js:
	npx prettier --tab-width=4 --write "**/*.{js,css,sass,scss}"

.PHONY: format-frontend
format-frontend: format-css-js format-html
