# AI Product Visualizer — interface

Dark-themed Streamlit interface for a product image analysis tool. This build is
frontend only: no model, API, cloud service or database is connected, and every
result shown is placeholder content used to preview layout and interaction.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Before running the app, copy `.env.example` to `.env` and set your Microsoft
Foundry project endpoint and API key:

```env
FOUNDRY_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
FOUNDRY_API_KEY=your_api_key
FOUNDRY_MODEL=gpt-4.1-mini
```

The app sends uploaded JPG, PNG, or WebP images to the Foundry Responses API
using the OpenAI-compatible client. The API key stays server-side and is never
shown in the UI.

## Structure

```
app.py                  entry point, routing, page headers
.streamlit/config.toml  dark theme + 10 MB upload limit
components/
  theme.py              design tokens, global CSS, UI primitives
  state.py              session state and navigation
  header.py             page header bar
  sidebar.py            navigation rail and model panel
  dashboard.py          home page
  upload.py             upload + preview + analyse trigger
  results.py            results dashboard
  qa.py                 question panel
  history.py            past analyses
  about.py              project overview
  media.py              locally drawn placeholder thumbnails, inline icons
data/
  mock_data.py          placeholder payloads
```

## Wiring up a model later

`data/mock_data.py` documents the shape the views expect:

```python
{
  "overview":   {"category", "product_type", "primary_color", "material", "style"},
  "attributes": {"colors": [{"name", "hex"}], "material", "shape", "style", "features"},
  "description": str,
  "confidence":  {"label": str, "score": int},
}
```

Two functions are the only places a real call needs to go:

- `components/upload.py` → `_run_analysis()` — replace the sleep with the image request.
- `components/qa.py` → `_answer_for()` — replace the lookup with the question request.

Nothing else in the view layer needs to change.
