## Change summary
Add a small static footer line reading "Built by the software factory POC" to the rota page. This is a presentation-only change within `templates/index.html`, requiring no new endpoints, data model changes, or outbound calls. The POC banner, `/health`, Dockerfile, and CI files remain untouched.

## Changes
1. **Add footer text to the rota page**
   - In `templates/index.html` (the template extending the base layout with the POC banner), add a footer element near the bottom of the page content containing the exact text `Built by the software factory POC`.
   - Keep it visually subdued (e.g. a `<footer>` or `<p class="footer">` with muted/small styling) so it does not interfere with the add form or entries list.
   - Do **not** modify the existing POC banner include, `/health` endpoint, Dockerfile, or CI workflow files.
   - **Acceptance criteria:**
     - Given I open `/`, When the page renders, Then the text `Built by the software factory POC` is visible at the bottom of the page.
     - Given the footer is added, When the page renders, Then the add form, entries list, Mark done, and Delete controls all still function and display as before.
     - Given the change is applied, When CI runs, Then the banner include, `/health`, Dockerfile, and CI files are unchanged.

## Tests to add or update
- Update the existing `GET /` test (or add a focused one) to assert the response body contains the string `Built by the software factory POC` and still returns 200.
- Re-confirm the existing `GET /health` test still passes (no change expected).

## Out of scope
- Any dynamic footer content (build numbers, timestamps, links).
- Changes to endpoints, the `rota_entries` data model, or the Firestore access layer.
- Styling frameworks or layout rework beyond minimal footer styling.
- Modifying the POC banner, `/health`, Dockerfile, or CI files.
