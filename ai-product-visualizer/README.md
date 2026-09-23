# AI Product Visualizer

AI Product Visualizer is a dark-themed Streamlit application that turns a product image into structured product insights. It uses the Microsoft Foundry Responses API through the OpenAI-compatible Python client and keeps API credentials on the server side.

The application can:

- Analyze a JPG, JPEG, PNG, or WebP product image.
- Identify visible details such as category, color, material, style, brand, model number, variant, and visible specifications.
- Generate an AI-written product description and confidence score.
- Show visual attributes, confidently identified details, and information that cannot be determined from the image.
- Answer questions about the uploaded product using image analysis.
- Search current prices and comparable products using web search.
- Preserve analyses in the current Streamlit session's history.

> Never commit `.env`, `.streamlit/secrets.toml`, API keys, or other credentials to source control.

## Contents

- [How the application works](#how-the-application-works)
- [Workflow](#workflow)
- [Detailed project walkthrough](#detailed-project-walkthrough)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Run locally](#run-locally)
- [Configuration and secrets](#configuration-and-secrets)
- [Using the application](#using-the-application)
- [Analysis response contract](#analysis-response-contract)
- [Responsible AI and Azure services](#responsible-ai-and-azure-services)
- [Deploy to Streamlit Community Cloud](#deploy-to-streamlit-community-cloud)
- [Troubleshooting](#troubleshooting)
- [Development guide](#development-guide)
- [Limitations and safe-use notes](#limitations-and-safe-use-notes)

## Quick workflow

```mermaid
flowchart LR
    A[Upload product image] --> B[Validate image]
    B --> C[Analyze with Microsoft Foundry]
    C --> D[View structured insights]
    D --> E{Next action}
    E --> F[Ask about product]
    E --> G[Search current prices]
    E --> H[Save in session history]
    F --> I[Image answer or web answer]
    G --> J[Comparable or exact-match results]
```

## How the application works

The application has four main user areas:

| Area | Purpose |
| --- | --- |
| Dashboard | Entry point with an overview of the product-analysis workflow and recent analyses. |
| Analyze Product | Accepts an image upload, validates it, and sends it to Microsoft Foundry. |
| Results | Displays structured analysis, identity fields, attributes, confidence, description, and price search. |
| History | Shows analyses stored in the current user session and allows an earlier result to be reopened. |

The question panel is available below an analysis. It classifies questions before sending them to the model:

- Questions about visible product details use the uploaded image.
- Price, availability, retailer, comparison, and similar-product questions use web search.
- Unrelated questions are rejected with a product-only response.

## Workflow

### End-to-end user workflow

```mermaid
flowchart TD
    A[Open application] --> B[Dashboard]
    B --> C[Analyze Product]
    C --> D{Upload valid image?}
    D -- No --> C
    D -- Yes --> E[Validate file type and size]
    E --> F[Preview image]
    F --> G[Click Analyze product]
    G --> H[Convert image to data URL]
    H --> I[Microsoft Foundry Responses API]
    I --> J{Successful response?}
    J -- No --> K[Show error and keep upload available]
    J -- Yes --> L[Parse strict JSON response]
    L --> M[Store analysis in session state]
    M --> N[Display results and confidence]
    N --> O[Ask product question]
    N --> P[Search current prices]
    N --> Q[Start new analysis]
    O --> R{Question type}
    R -- Image/product detail --> S[Responses API with image]
    R -- Current market information --> T[Responses API with web search]
    R -- Unrelated --> U[Product-only refusal]
    P --> T
    Q --> C
```

### Analysis workflow

```mermaid
sequenceDiagram
    participant User
    participant Streamlit as Streamlit UI
    participant Service as services/ai_service.py
    participant Foundry as Microsoft Foundry

    User->>Streamlit: Upload product image
    Streamlit->>Streamlit: Validate format and 10 MB limit
    User->>Streamlit: Click Analyze product
    Streamlit->>Service: analyze_product(bytes, MIME type)
    Service->>Service: Read endpoint, key, and model
    Service->>Service: Encode image as data URL
    Service->>Foundry: Responses API request with image and JSON schema
    Foundry-->>Service: Structured product analysis
    Service->>Service: Parse JSON
    Service-->>Streamlit: Analysis dictionary
    Streamlit->>Streamlit: Save result in session state and history
    Streamlit-->>User: Render overview, attributes, description, and confidence
```

### Question-routing workflow

```mermaid
flowchart LR
    A[User question] --> B{Contains unrelated topic?}
    B -- Yes --> C[Return product-only refusal]
    B -- No --> D{Needs current web information?}
    D -- No --> E[Answer from uploaded image]
    D -- Yes --> F[Search current web information]
    E --> G[Append answer to session Q&A]
    F --> G
    C --> G
```

## Detailed project walkthrough

This section describes the complete runtime workflow in the order a user, presenter, or developer can explain it.

### Phase 1: Application startup

1. Streamlit starts `app.py`.
2. `st.set_page_config()` sets the page title, icon, wide layout, and expanded sidebar.
3. `main()` calls `init_state()` from `components/state.py`.
4. `init_state()` creates the per-user session values used by the application, including:
   - Current page.
   - Current uploaded image.
   - Uploaded image bytes and MIME type.
   - Current analysis result.
   - Analysis source filename.
   - Q&A messages.
   - Price-search result.
   - History entries.
   - Theme mode and toast messages.
5. `theme.inject_css()` applies the custom visual design.
6. `render_sidebar()` displays navigation and the theme control.
7. `render_header()` displays the title and subtitle for the selected page.
8. `app.py` routes to the selected page renderer.

```mermaid
flowchart TD
    A[streamlit run app.py] --> B[set page configuration]
    B --> C[initialize session state]
    C --> D[inject theme CSS]
    D --> E[render sidebar]
    E --> F[render page header]
    F --> G{Current page}
    G --> H[Dashboard]
    G --> I[Analyze Product]
    G --> J[History]
    G --> K[About]
```

### Phase 2: Dashboard and navigation

The Dashboard is the starting page. It explains the product-analysis experience and provides actions to begin a new analysis or view session history.

Navigation is controlled by `st.session_state.page`. When the user clicks a sidebar item, `components/sidebar.py` updates that value and Streamlit reruns the script. On the next rerun, `app.py` renders the selected page.

Important Streamlit behavior: a button click causes a rerun from the top of `app.py`. The application therefore stores important values in `st.session_state` instead of relying on local variables from a previous run.

### Phase 3: Image upload and validation

The upload page is rendered by `components/upload.py`.

1. The user opens **Analyze Product**.
2. `st.file_uploader()` accepts JPG, JPEG, PNG, and WebP files.
3. The uploaded file is checked against the 10 MB limit.
4. Pillow opens the file and loads the image to confirm it is readable.
5. The image is saved to `st.session_state.upload` for preview.
6. The interface displays the filename, dimensions, file size, format, and image preview.
7. The **Analyze product** button becomes available.

If validation fails, the app displays an error and stops before making an external API request.

### Phase 4: AI image analysis

When the user clicks **Analyze product**, `_run_analysis()` in `components/upload.py` performs the following steps:

1. Reads the uploaded file bytes and MIME type.
2. Calls `analyze_product()` in `services/ai_service.py`.
3. Reads `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_API_KEY`, and `FOUNDRY_MODEL`.
4. Normalizes the project endpoint so it ends in `/openai/v1`.
5. Creates an OpenAI-compatible client pointed at the Microsoft Foundry project endpoint.
6. Encodes the image as a base64 data URL.
7. Sends the image, analysis instructions, and strict JSON schema to the Foundry Responses API.
8. The model analyzes only visible evidence and returns structured JSON.
9. The service parses the response using `json.loads()`.
10. If parsing fails, the user receives an error instead of an incomplete result.
11. On success, the result is stored in session state.
12. The uploaded bytes and MIME type are retained for later image-based Q&A.
13. A history entry is inserted at the beginning of the current session history.
14. The app triggers a rerun and displays the Results page.

The main analysis function is:

```text
analyze_product(image_bytes, mime_type) -> analysis dictionary
```

The result must contain `overview`, `identity`, `attributes`, `description`, `confidence`, `confidently_identified`, and `cannot_determine`.

### Phase 5: Results rendering

The Results page is rendered by `components/results.py`.

1. The stored analysis is read from `st.session_state.analysis`.
2. The source image is displayed.
3. The overview is rendered as key-value rows.
4. Identity fields are shown as editable inputs:
   - Brand.
   - Product name.
   - Model number.
   - Variant.
   - Visible specifications.
5. The confidence label and score are displayed with a visual meter.
6. Visual attributes are rendered as chips and color swatches.
7. The generated description is displayed.
8. The application separates confidently identified information from information it cannot determine.
9. The market-price search section is displayed.
10. The Q&A panel is displayed below the result.

The user can correct identity fields before performing a market search. This creates an important human-in-the-loop step: the model proposes an identity, while the user can review it before current-market lookup.

### Phase 6: Current-price search

The price-search flow starts from the Results page.

1. The user enters a market or location, defaulting to India.
2. The app checks whether brand, product name, and model number are all present.
3. If all three are available, the request is treated as an exact-match search.
4. If the model number is missing or unverified, the request is treated as a comparable-product search.
5. `search_product_prices()` sends the product identity, location, and match mode to Foundry.
6. The Responses API is instructed to use hosted web search.
7. Search is restricted to configured retail domains such as Amazon India, Flipkart, Croma, and Reliance Digital.
8. The returned answer is stored in `st.session_state.web_search_result`.
9. The result is rendered below the search button.

The application deliberately distinguishes exact matches from comparisons so that a similar product is not presented as the same product.

### Phase 7: Product Q&A

The Q&A flow is implemented in `components/qa.py`.

1. The user enters a question or selects a suggested question.
2. The question is stored as a user message in session state.
3. `_is_product_question()` checks whether the question is related to the uploaded product.
4. If the question is unrelated, the app returns: `I can only answer questions about the uploaded product.`
5. If the question is product-related, the app checks for web-search terms.
6. Questions about appearance, visible attributes, material, color, shape, or features call `answer_product_question()`.
7. Questions about price, availability, retailers, comparison, alternatives, or similar products call `answer_web_question()`.
8. The answer is appended to the Q&A history with a source label.
9. Streamlit reruns and displays the conversation.

```mermaid
sequenceDiagram
    participant U as User
    participant Q as components/qa.py
    participant S as services/ai_service.py
    participant F as Microsoft Foundry

    U->>Q: Submit question
    Q->>Q: Product-topic filter
    alt Unrelated question
        Q-->>U: Product-only refusal
    else Product detail question
        Q->>S: answer_product_question(image, question)
        S->>F: Responses API with image
        F-->>S: Image-grounded answer
        S-->>Q: Answer
        Q-->>U: Display image-analysis answer
    else Current market question
        Q->>S: answer_web_question(identity, question)
        S->>F: Responses API with web search
        F-->>S: Current-information answer
        S-->>Q: Answer
        Q-->>U: Display web-search answer
    end
```

### Phase 8: History and reset

History is session-scoped rather than database-backed.

- After a successful analysis, `upload.py` creates a history entry and inserts it at index zero.
- `history.py` displays the available entries.
- Selecting an entry copies its analysis into `st.session_state.analysis`.
- The previous result can be reopened without uploading the image again in the current session.
- **New analysis** calls `reset_analysis()` in `components/state.py`.
- Reset clears the active analysis, image bytes, MIME type, Q&A messages, and price-search output.

### Complete data lifecycle

```mermaid
flowchart TB
    IMG[Uploaded image] --> VALIDATE[Format and size validation]
    VALIDATE --> BYTES[Image bytes and MIME type]
    BYTES --> ENCODE[Base64 data URL]
    ENCODE --> API[Foundry Responses API]
    API --> JSON[Strict analysis JSON]
    JSON --> STATE[st.session_state.analysis]
    STATE --> RESULT[Results renderer]
    STATE --> HISTORY[Session history]
    BYTES --> QA[Image-based Q&A]
    STATE --> IDENTITY[Editable product identity]
    IDENTITY --> SEARCH[Price and web search]
    SEARCH --> WEBRESULT[Web-search result]
    WEBRESULT --> STATE
```

### Suggested presentation script

Use the following script when explaining the project:

> “AI Product Visualizer is a Streamlit application for extracting useful product insights from an image. When the application starts, `app.py` initializes the page configuration, session state, theme, sidebar, and selected page. The user begins on the Dashboard and navigates to Analyze Product.
>
> On the upload page, the user selects a JPG, JPEG, PNG, or WebP image. The application validates the format, confirms that the image is readable, enforces the 10 MB limit, and shows a preview before any AI call is made.
>
> When the user clicks Analyze product, the upload component sends the image bytes to the service layer. The service layer reads the Microsoft Foundry endpoint, API key, and model name from secure configuration. It converts the image into a data URL and sends it to the Foundry Responses API with analysis instructions and a strict JSON schema.
>
> The model is instructed to use visible evidence only. It must not guess hidden specifications or unreadable model numbers. The response contains an overview, product identity, visual attributes, description, confidence score, confidently identified details, and details that cannot be determined.
>
> After the response is validated, the application stores it in Streamlit session state and adds it to the current session history. The Results page then displays the image, overview, editable identity fields, confidence meter, attribute chips, generated description, and uncertainty information.
>
> The user can correct the detected identity before searching current prices. If brand, product name, and model number are available, the application can request an exact-match search. If the model number is missing, the application explicitly labels the results as comparable products.
>
> The user can also ask questions. Product-appearance questions are answered from the uploaded image. Current questions about price, availability, retailers, or comparisons are routed through Foundry web search. Unrelated questions are filtered and refused so the assistant remains focused on the uploaded product.
>
> Finally, the user can reopen analyses from the current session history or start a new analysis. The project uses Microsoft Foundry for model access, the Responses API for structured output, and hosted web search for current market information. Responsible-AI controls are applied through evidence-only instructions, uncertainty fields, confidence scores, topic filtering, exact-match labeling, input validation, and secure credential handling.”

### File-by-file execution map

| Runtime event | File | Responsibility |
| --- | --- | --- |
| App starts | `app.py` | Configure Streamlit and route pages. |
| Session initializes | `components/state.py` | Create and reset user session values. |
| Navigation click | `components/sidebar.py` | Change the active page and theme mode. |
| Upload selected | `components/upload.py` | Validate, preview, and read image bytes. |
| Analyze clicked | `components/upload.py` | Call the analysis service and save the result. |
| AI analysis request | `services/ai_service.py` | Build the Foundry client, prompt, image input, and schema. |
| Results shown | `components/results.py` | Render structured analysis and identity editing. |
| Price search clicked | `components/results.py` and `services/ai_service.py` | Search current market information. |
| Q&A submitted | `components/qa.py` | Filter and route questions. |
| History selected | `components/history.py` | Restore a session analysis. |
| Theme applied | `components/theme.py` and `.streamlit/config.toml` | Control colors, layout styling, and Streamlit settings. |

## Architecture

```mermaid
flowchart TB
    UI[Streamlit presentation layer\napp.py and components/] --> STATE[Session state\ncomponents/state.py]
    UI --> SERVICE[AI service layer\nservices/ai_service.py]
    UI --> MOCK[data and sample history\ndata/mock_data.py]
    SERVICE --> F[Microsoft Foundry\n/openai/v1/responses]
    F --> V[Vision analysis\nStructured JSON]
    F --> W[Hosted web search\nPrices and current information]
    CONFIG[.streamlit/config.toml] --> UI
    ENV[Environment variables or Streamlit secrets] --> SERVICE
```

### Main components

- `app.py` initializes the page, injects the theme, renders navigation, and routes between pages.
- `components/` contains the UI layer, page sections, session state, styling, upload flow, results, history, and Q&A.
- `services/ai_service.py` is the integration boundary for Microsoft Foundry. It contains image analysis, image-based Q&A, product-price search, and web Q&A.
- `data/mock_data.py` contains sample data used to populate the initial experience and documents the expected UI data shape.
- `.streamlit/config.toml` defines the theme, upload limit, toolbar behavior, and error-detail setting.

## Project structure

```text
ai-product-visualizer/
├── app.py                         # Streamlit entry point
├── requirements.txt               # Python dependencies
├── README.md                      # This guide
├── .gitignore                     # Excludes secrets and local environments
├── .streamlit/
│   └── config.toml                # Theme and Streamlit server settings
├── components/
│   ├── about.py                   # About page
│   ├── dashboard.py               # Dashboard page
│   ├── header.py                  # Shared page header
│   ├── history.py                 # Session history page
│   ├── media.py                   # Image and media helpers
│   ├── qa.py                      # Product Q&A and question routing
│   ├── results.py                 # Analysis results and price search
│   ├── sidebar.py                 # Navigation and theme controls
│   ├── state.py                   # Session-state initialization/reset
│   ├── theme.py                   # Design tokens and UI helpers
│   └── upload.py                  # Upload, validation, and analysis trigger
├── data/
│   ├── __init__.py
│   └── mock_data.py               # Sample data and history records
└── services/
    ├── __init__.py
    └── ai_service.py              # Microsoft Foundry API integration
```

## Requirements

- Python 3.10 or newer.
- A Microsoft Foundry project with a vision-capable model deployment.
- A Microsoft Foundry project endpoint and API key.
- The model name used by the Foundry project.
- Network access from the deployment environment to the Foundry endpoint.

Python packages are listed in [`requirements.txt`](requirements.txt): `streamlit`, `pillow`, `openai`, and `python-dotenv`.

## Run locally

Open a terminal in the folder containing `app.py`.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

The default local URL is `http://localhost:8501`. To use a different port:

```bash
streamlit run app.py --server.port 8502
```

## Configuration and secrets

### Local development with `.env`

Create a local `.env` file beside `app.py`:

```env
FOUNDRY_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
FOUNDRY_API_KEY=your_api_key
FOUNDRY_MODEL=gpt-4.1-mini
```

The application loads this file using `python-dotenv`. The `.env` file is ignored by Git and must remain local.

### Variable reference

| Variable | Required | Description |
| --- | --- | --- |
| `FOUNDRY_PROJECT_ENDPOINT` | Yes | Microsoft Foundry project endpoint. The service appends `/openai/v1` when needed. |
| `FOUNDRY_API_KEY` | Yes | API key used by the server to authenticate with Foundry. |
| `FOUNDRY_MODEL` | Yes | Model deployment name, for example `gpt-4.1-mini`. |

### Streamlit secrets

For hosts that use Streamlit secrets, create `.streamlit/secrets.toml` locally only when needed:

```toml
FOUNDRY_PROJECT_ENDPOINT = "https://your-resource.services.ai.azure.com/api/projects/your-project"
FOUNDRY_API_KEY = "your_api_key"
FOUNDRY_MODEL = "gpt-4.1-mini"
```

Do not commit this file. It is already excluded by `.gitignore`.

## Using the application

### 1. Upload an image

1. Open **Analyze Product**.
2. Upload one product image.
3. Use a clear image with one product, good lighting, and minimal occlusion.
4. Keep the file at or below 10 MB.
5. Review the preview and click **Analyze product**.

### 2. Review the analysis

The results page contains:

- Product overview.
- Editable product identity fields.
- AI confidence label and score.
- Colors, material, shape, style, and features.
- Generated product description.
- Details confidently identified by the model.
- Details the model cannot determine from the image.

The identity fields can be corrected before running a market search. This is especially important when a brand, product name, variant, or model number is uncertain.

### 3. Search current prices

1. Review or correct the identity fields.
2. Enter the market or location, which defaults to `India`.
3. Click **Search current prices**.

If brand, product name, and model number are present, the app requests an exact-match search. Otherwise, results are treated as comparable products rather than confirmed matches.

### 4. Ask a question

Use the Q&A section below the results. Questions about appearance and visible attributes are answered from the uploaded image. Questions involving price, availability, retailers, comparisons, or similar products are routed through web search.

The application intentionally refuses unrelated topics such as programming, homework, politics, sports, recipes, and song lyrics.

### 5. Start over or reopen history

- Click **New analysis** to clear the active result and upload another image.
- Open **History** to reopen an earlier result from the current session.
- History is stored in Streamlit session state; it is not a permanent database.

## Analysis response contract

The Foundry vision request uses a strict JSON schema. The expected top-level response is:

```json
{
  "overview": {
    "Category": "string",
    "Product Type": "string",
    "Primary Color": "string",
    "Material": "string",
    "Style": "string"
  },
  "identity": {
    "brand": "string",
    "product_name": "string",
    "model_number": "string",
    "variant": "string",
    "specifications": ["string"]
  },
  "attributes": {
    "Colors": [{"name": "string", "hex": "#000000"}],
    "Material": ["string"],
    "Shape": ["string"],
    "Style": ["string"],
    "Features": ["string"]
  },
  "description": "string",
  "confidence": {"label": "string", "score": 0},
  "confidently_identified": ["string"],
  "cannot_determine": ["string"]
}
```

The schema and prompt are defined in `services/ai_service.py`. If the response contract changes, update the schema and result renderer together.

## Responsible AI and Azure services

This project is designed to provide useful product insights while making uncertainty visible and limiting the system to its intended purpose. The responsible-AI controls are implemented across the application prompt, response schema, question router, and market-search presentation.

### Guardrails currently implemented

| Guardrail | Implementation | User benefit |
| --- | --- | --- |
| Evidence-only analysis | The Foundry system instruction tells the model to report only what can reasonably be determined from the image. | Reduces invented specifications, dimensions, model numbers, brand details, and performance claims. |
| Explicit uncertainty | The response schema includes `cannot_determine`; unreadable model numbers must be returned as empty instead of guessed. | Makes missing or uncertain information visible. |
| Confidence display | Every analysis includes a confidence label and a score from 0 to 100. | Helps users judge how much to rely on the result. |
| Product-only Q&A | The application filters unrelated topics such as programming, homework, politics, sports, recipes, and lyrics. | Keeps the assistant within its intended product-analysis scope. |
| Separate image and web reasoning | Visible product questions use the uploaded image; current price and availability questions use web search. | Reduces confusion between visual evidence and changing market information. |
| Exact-match protection | A market search is marked as exact only when brand, product name, and model number are available. Otherwise results are labeled comparable or not exact. | Prevents similar products from being presented as the identified product. |
| Input validation | Uploads are limited to supported image formats and 10 MB. | Reduces malformed input and resource-abuse risk. |
| Secret protection | API credentials are loaded from local environment variables or deployment secrets and are excluded from Git. | Keeps credentials out of source code and the user interface. |

### Microsoft Azure and Foundry capabilities used

The application uses a Microsoft Foundry project endpoint through the OpenAI-compatible Responses API:

```text
{FOUNDRY_PROJECT_ENDPOINT}/openai/v1/responses
```

The configured Azure service capabilities are:

1. **Microsoft Foundry project endpoint** — provides the project-scoped model access and authentication boundary.
2. **Vision-capable Foundry model** — analyzes the uploaded product image and returns the strict structured JSON contract documented above.
3. **Responses API structured output** — constrains analysis responses to the required schema.
4. **Hosted web search tool** — supports current price, retailer, availability, and comparable-product questions.

The integration is centralized in `services/ai_service.py`. The application does not expose the API key to the browser.

### Responsible-use expectations

AI output should be treated as an assistive estimate, not as proof of identity, authenticity, safety, compliance, warranty, or technical specifications. Users should verify important information against the manufacturer or retailer, especially before making a purchase or safety-related decision. Current prices and availability can change after a result is generated.

The current repository implements application-level guardrails and Foundry prompt/schema controls. A separate Azure AI Content Safety moderation call is not currently wired into the codebase; it should be added if the product is expanded to accept free-form user content or support higher-risk use cases.

## Deploy to Streamlit Community Cloud

The repository is ready for Streamlit Community Cloud. The repository root should contain `app.py`, `requirements.txt`, `.streamlit/config.toml`, `components/`, `data/`, and `services/`.

1. Push the project to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select **Create app**.
4. Choose the GitHub repository and the `main` branch.
5. Set the main file to `app.py`.
6. Open **Advanced settings**.
7. Set the Python version used by your local environment, preferably Python 3.12 for a new deployment.
8. Add the following to the **Secrets** field:

   ```toml
   FOUNDRY_PROJECT_ENDPOINT = "https://your-resource.services.ai.azure.com/api/projects/your-project"
   FOUNDRY_API_KEY = "your_api_key"
   FOUNDRY_MODEL = "gpt-4.1-mini"
   ```

9. Click **Deploy**.

Streamlit Cloud installs dependencies from `requirements.txt` and keeps values entered in the Secrets field outside the repository. If the app is inside a subdirectory, select that subdirectory's `app.py` and ensure the dependency file is either at the repository root or beside the entry point.

## Troubleshooting

### `FOUNDRY_API_KEY is missing`

Confirm that all three variables are present in your local `.env` or deployment secrets. Restart the Streamlit process after changing secrets.

### `Could not analyze the image`

Check that the Foundry endpoint is correct, the API key can access the project, the model deployment name matches `FOUNDRY_MODEL`, the model supports image input and structured Responses API output, and the deployment environment can reach the endpoint.

### `Foundry returned invalid analysis JSON`

The model did not satisfy the strict response schema. Verify that the configured model supports structured JSON output and inspect the model/deployment configuration before changing the UI contract.

### Price search fails

Price search requires a model and Foundry configuration that support the hosted `web_search` tool. Confirm that web search is enabled for the project and that the deployment has outbound network access.

### The app cannot find modules such as `components` or `services`

Run Streamlit from the project directory containing `app.py`, or configure the deployment entry point to use that directory. Do not run the command from the parent workspace if the project is nested.

### Uploads are rejected

The application accepts JPG, JPEG, PNG, and WebP files up to 10 MB. The limit is configured in both `components/upload.py` and `.streamlit/config.toml`; keep those values aligned if the limit changes.

## Development guide

### Add or change a page

1. Add a renderer in `components/`.
2. Add its page name and heading in `app.py`.
3. Add navigation behavior in `components/sidebar.py` if needed.
4. Keep per-user values in `st.session_state`, initialized in `components/state.py`.

### Change the Foundry integration

Keep external API calls inside `services/ai_service.py`. The UI should call service functions rather than constructing API clients directly. This keeps credentials, endpoint normalization, prompts, schemas, and error handling in one place.

### Change the analysis schema

Update all of the following together:

1. `ANALYSIS_SCHEMA` in `services/ai_service.py`.
2. `ANALYSIS_INSTRUCTIONS` if the model needs new guidance.
3. `components/results.py` to render the new fields.
4. `data/mock_data.py` if sample data is used for the new field.
5. This README's [analysis response contract](#analysis-response-contract).

### Local checks

```bash
python -m compileall app.py components data services
streamlit run app.py
```

Before opening a pull request, verify that no `.env` or secrets file is staged, upload and analysis work, Q&A and price search work, history and reset work, and schema changes are reflected in the UI and documentation.

## Limitations and safe-use notes

- The model can only infer information visible in the uploaded image. It should not be treated as an authoritative source for hidden specifications, authenticity, safety, warranty, or legal claims.
- A readable model number is required for a reliable exact-match market search. If it is missing or uncertain, the application labels results as comparable products.
- Price and availability information changes over time and can vary by location, taxes, shipping, seller, and condition.
- Uploaded image bytes and analysis state are held in the active Streamlit session. The application does not provide durable database storage.
- API keys are server-side configuration values. Never print them, expose them in the UI, commit them, or include them in screenshots or logs.
