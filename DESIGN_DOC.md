# SQL Query Bot Technical Design Document

## Overview
The SQL Query Bot is a web application that converts natural language queries into SQL queries, executes them on a SQLite database (`combined.db`), and displays results in a Gradio interface. It uses the Together AI API for SQL generation, FastAPI for the backend, and Gradio for the frontend.

## Architecture
- **Frontend:** `interface.py` (Gradio) provides a web UI at `http://127.0.0.1:7860`, sending GET requests to the backend.
- **Backend:** `app.py` (FastAPI) runs on `http://127.0.0.1:8000`, exposing a `/query` endpoint to process queries and return JSON.
- **Database:** `combined.db` (SQLite) stores `sales` and `orders` tables, managed by `setup_dbs.py` and verified by `verify_combined_db.py` in Your Project Directory.
- **External Service:** Together AI API (`https://api.together.xyz/inference`) generates SQL queries based on natural language.

## Database Schema
- **combined.db**
  - **sales Table:**
    - `id`: INTEGER (auto-incrementing primary key)
    - `customer_name`: TEXT
    - `revenue`: REAL
    - `region`: TEXT
    - `sale_date`: TEXT
  - **orders Table:**
    - `order_id`: INTEGER (auto-incrementing primary key)
    - `customer_name`: TEXT
    - `order_amount`: REAL
    - `product`: TEXT
    - `order_date`: TEXT
- Created and populated by `setup_dbs.py` with 50 records each.

## API Flow
1. **User Input:** Enters “top 3 customers by revenue” in Gradio.
2. **Gradio Request:** Sends `GET /query?query=top%203%20customers%20by%20revenue` to FastAPI.
3. **FastAPI Processing:**
   - Extracts `query` parameter.
   - Calls `generate_and_execute_sql` to generate SQL via Together AI.
   - Executes SQL on `combined.db` using `execute_query`.
   - Returns JSON: `{"sql": "...", "results": {"columns": [...], "data": [...]}}`.
4. **Gradio Display:** Formats and shows results in the “Results” textbox.

## Code Details
- **backend.py:** Original terminal script for testing SQL generation (not used in web app but serves as reference).
- **app.py:** FastAPI backend with `/query` endpoint, using Together AI and SQLite.
- **interface.py:** Gradio frontend for user interaction.
- **setup_dbs.py:** Creates and populates `combined.db`.
- **verify_combined_db.py:** Verifies database contents.

## Dependencies
- `requests`: For API calls to Together AI
- `fastapi`: For web backend
- `uvicorn`: To run FastAPI server
- `gradio`: For web interface
- `sqlite3`: Built into Python for database operations

## Configuration
- **API Key:** Stored as `Bearer API_KEY` in code (actual key in `.env`, not committed to version control).
- **Database:** `combined.db` in Your Project Directory.

## Performance Considerations
- Together AI API latency may affect response time; consider caching or optimizing prompts.
- SQLite is efficient for small datasets but may scale poorly for large data; monitor performance for growth.

## Future Enhancements
- Add authentication for the `/query` endpoint.
- Implement caching for frequent queries.
- Enhance Gradio UI with styling or additional features (e.g., query history, error alerts).

## Contact
For technical questions, contact Support Team at nithi.kkv@gmail.com.