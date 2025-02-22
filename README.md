# SQL Query Bot

## Overview
The SQL Query Bot is a web-based application that allows users to input natural language queries (e.g., "top 3 customers by revenue") and generates/executes corresponding SQL queries on a SQLite database (`combined.db`) containing `sales` and `orders` tables. It uses the Together AI API for SQL generation, FastAPI for the backend, and Gradio for the frontend.

## Features
- Generates SQL queries from natural language inputs.
- Executes queries on `combined.db` (sales and orders data).
- Displays results in a user-friendly Gradio web interface.
- Supports queries for sales (revenue, region, dates), orders (amounts, products), and combined data.

## Prerequisites
- Python 3.8 or higher
- Virtual environment (`venv`)

## Installation
1. Clone or download this repository to Your Project Directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate

## Getting Help
If you encounter issues or have questions, open an issue on this GitHub repository or contact the Support Team at anonymous@example.com.

## Contributing
Contributions are welcome! Fork this repository, make changes, and submit a pull request. Please follow the coding style in `DESIGN_DOC.md` and update documentation as needed.
