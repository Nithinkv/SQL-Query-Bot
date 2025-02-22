import gradio as gr
import requests

# FastAPI endpoint URL
API_URL = "http://127.0.0.1:8000/query"

def query_sql(user_query):
    try:
        # Send GET request to FastAPI endpoint with the query as a parameter
        response = requests.get(f"{API_URL}?query={user_query}")
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()

        # Format the result for display
        output = f"Generated SQL Query: {result['sql']}\n\n"
        if "error" in result:
            output += f"Error: {result['error']}"
        else:
            output += "Results:\n"
            output += f"Columns: {', '.join(result['results']['columns'])}\n"
            for row in result['results']['data']:
                output += str(row) + "\n"
        return output
    except requests.exceptions.RequestException as e:
        return f"Error connecting to API: {str(e)}"
    except Exception as e:
        return f"Error processing query: {str(e)}"

# Create Gradio interface
interface = gr.Interface(
    fn=query_sql,
    inputs=gr.Textbox(lines=2, placeholder="Enter your query (e.g., 'top 3 customers by revenue')"),
    outputs=gr.Textbox(lines=10, label="Results"),
    title="SQL Query Bot",
    description="Enter a natural language query to generate and execute a SQL query on the combined database (sales and orders tables)."
)

if __name__ == "__main__":
    interface.launch()