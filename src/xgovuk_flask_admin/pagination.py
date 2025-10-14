def govuk_pagination_params_builder(page_zero_indexed, total_pages, url_generator):
    """Builds the `params` argument for govukPagination based on govuk-frontend-jinja.

    This is fed by values from Flask-Admin's pagination, which provides:
        arg 1 (`page`) as a 0-indexed reference to the current page; but
        arg 2 (`pages`) as the number of total pages rather than the max page as a 0-indexed thing
    """
    component_params = {}

    if page_zero_indexed != 0:
        component_params["previous"] = {"href": url_generator(page_zero_indexed - 1)}

    if page_zero_indexed + 1 != total_pages:
        component_params["next"] = {"href": url_generator(page_zero_indexed + 1)}

    if total_pages <= 3:
        items = [
            {
                "number": x + 1,
                "current": page_zero_indexed == x,
                "href": url_generator(x),
            }
            for x in range(0, total_pages)
        ]

    else:
        items = []
        num_pages_around_current = 2

        pages_to_show = {0, page_zero_indexed, total_pages - 1}
        for x in range(1, num_pages_around_current + 1):
            pages_to_show.add(max(0, page_zero_indexed - x))
            pages_to_show.add(min(total_pages - 1, page_zero_indexed + x))

        last = -1
        for curr in sorted(pages_to_show):
            if last + 1 < curr:
                items.append({"ellipsis": True})

            items.append(
                {
                    "number": curr + 1,
                    "current": page_zero_indexed == curr,
                    "href": url_generator(curr),
                }
            )
            last = curr

    component_params["items"] = items
    component_params["classes"] = "govuk-!-text-align-center"

    return component_params
