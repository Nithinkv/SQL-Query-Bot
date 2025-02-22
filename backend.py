import requests
import sqlite3

# Function to get database schema for a specific table
def get_schema_info(table_name):
    conn = sqlite3.connect("combined.db")
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return f"Table: {table_name}\nColumns: {', '.join(columns)}\n"

# Function to execute the SQL query on a specific table in combined.db
def execute_query(sql, table_name):
    conn = sqlite3.connect("combined.db")
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        return {"columns": column_names, "data": results}
    except sqlite3.Error as e:
        return {"error": f"SQLite Error: {str(e)}"}
    finally:
        conn.close()

# Function to clean up the SQL query
def clean_sql_query(text):
    text = text.replace("SQL Query:", "").strip()
    text = text.replace("```", "").strip()
    text = text.replace("\n", " ").strip()
    if text.endswith(";"):
        text = text[:-1]
    # Remove any unexpected backslashes, quotes, explanatory text, or fix spacing
    text = text.replace("\\", "").replace("\"", "").replace("'", "")
    text = " ".join(text.split())  # Normalize spaces (replace multiple spaces with single space)
    # Ensure lowercase keywords and quoted product values in WHERE clauses
    text = text.lower().replace("select", "select").replace("where", "where").replace("from", "from").replace("join", "join")
    if "where o.product =" in text:
        text = text.replace("where o.product =", "where o.product = '").replace(";", "'")
    elif "where product =" in text:
        text = text.replace("where product =", "where product = '").replace(";", "'")
    return text

def generate_and_execute_sql(user_query):
    # Determine which table to use based on the query
    use_sales = any(keyword in user_query.lower() for keyword in ["sales", "revenue", "region", "sale"])
    use_orders = any(keyword in user_query.lower() for keyword in ["orders", "order", "amount", "product"])

    # Get schema info for relevant tables
    schemas = ""
    if use_sales:
        schemas += get_schema_info("sales") + "\n"
    if use_orders:
        schemas += get_schema_info("orders") + "\n"
    if not schemas:
        schemas = get_schema_info("sales") + "\n" + get_schema_info("orders") + "\n"  # Default to both

    # Build the prompt with focused SQLite-specific rules for both tables, ensuring quoted products in joins
    prompt = (
        f"You are an SQL expert for SQLite. Convert the user's request into a SINGLE valid SQLite query based on these database schemas, outputting ONLY the SQL query itself—NO explanations, comments, descriptions, or additional text of any kind (e.g., no 'To determine...', no notes, just the SQL query ending with a semicolon).\n\n"
        f"{schemas}\n"
        f"User Query: {user_query}\n\n"
        f"Rules:\n"
        f"- Use 'sales' table in combined.db for queries about sales, revenue, region, or sale dates. Only use columns: customer_name, revenue, region, sale_date.\n"
        f"- Use 'orders' table in combined.db for queries about orders, order amounts, products, or order dates. Only use columns: customer_name, order_amount, product, order_date.\n"
        f"- Do NOT use 'order_id' or 'id' in SELECT statements unless explicitly requested (e.g., 'show order IDs'), as they are auto-incrementing primary keys and may not be directly selectable.\n"
        f"- If the query contains 'more than', 'less than', 'equal to', use `where`.\n"
        f"- If the query asks for the 'highest' or 'lowest', use `order by revenue desc` or `asc` for sales, or `order by order_amount desc` or `asc` for orders.\n"
        f"- If the query asks for the 'top' or 'most', use `order by revenue desc limit X` for sales or `order by order_amount desc limit X` for orders, where X is the number specified (default to 3 if not specified).\n"
        f"- If the query asks for the 'least' or 'smallest', use `order by revenue asc limit X` for sales or `order by order_amount asc limit X` for orders, where X is the number specified (default to 3 if not specified).\n"
        f"- If it asks for 'total customers', interpret as the total unique customers from the sales table: select count(distinct customer_name) as total_customers from sales;\n"
        f"- If it asks for 'total orders', interpret as the total unique customers from the orders table: select count(distinct customer_name) as total_orders from orders;\n"
        f"- If it asks for 'total sales table' or 'total sales', interpret as the total revenue from the sales table: select sum(revenue) as total_sales from sales;\n"
        f"- If it asks for 'who sold more', interpret as 'top customers by total revenue' from the sales table: select customer_name, sum(revenue) as total_revenue from sales group by customer_name order by total_revenue desc limit 5;\n"
        f"- If it asks for 'who bought [product]', 'which customer bought [product]', 'who has [product]', 'who have [product]', or 'who brought [product]' (treating 'have', 'has', or 'brought' as typos for 'bought'), interpret as finding customers who ordered that exact product and their sales revenue by joining the tables. Use `select distinct s.customer_name, s.revenue from sales s join orders o on s.customer_name = o.customer_name where o.product = '[product]'` (e.g., `where o.product = 'monitor'`), ensuring the product value is enclosed in single quotes (e.g., `where o.product = 'monitor'`).\n"
        f"- If the query mentions both 'product' and 'revenue' (e.g., 'product and revenue'), join the 'sales' and 'orders' tables on customer_name to show customers with both sales revenue and product purchases: use `select distinct s.customer_name, s.revenue, o.product from sales s join orders o on s.customer_name = o.customer_name`.\n"
        f"- Always generate a proper SQLite query, no explanations.\n"
        f"- Always verify column names match the schemas provided EXACTLY, and only use exact column names listed (e.g., customer_name, not CustomerName or client_namn).\n"
        f"- Ensure column names, table names, and SQL keywords (e.g., select, from, where, group by, order by, distinct, as, count, sum, join) are lowercase and match the schema exactly (e.g., customer_name, sales, orders, not CUSTOMER_NAME, SALES, ORDERS).\n"
        f"- Ensure proper spacing and syntax: use SINGLE spaces between all keywords, identifiers, and operators (e.g., `select distinct s.customer_name, s.revenue from sales s join orders o on s.customer_name = o.customer_name`, not `selectdisticts.customer_names.revenuefromsalessjoinordersoonscustomer_nameo.customer_name`), with no special characters (e.g., backslashes, quotes) except as needed for strings in `where` clauses. Ensure string literals (e.g., product values) are enclosed in single quotes (e.g., `where o.product = 'monitor'`).\n"
        f"- EVERY select query MUST include a `from` clause with the correct table name (e.g., `from sales` or `from orders`). For joins, use `from sales s join orders o on s.customer_name = o.customer_name`.\n"
        f"- Handle numeric modifiers in queries (e.g., 'top 3 customers by 20 revenue') by interpreting '20 revenue' as 'revenue over 20' or similar thresholds, and always include `from`.\n\n"
        f"Example Outputs (all must be lowercase, properly spaced, and end with a semicolon):\n"
        f"- User: 'Who sold more than 100?' → select customer_name from sales where revenue > 100;\n"
        f"- User: 'Top 3 customers by revenue?' → select customer_name, sum(revenue) as total_revenue from sales group by customer_name order by total_revenue desc limit 3;\n"
        f"- User: 'Who bought monitor?' → select distinct s.customer_name, s.revenue from sales s join orders o on s.customer_name = o.customer_name where o.product = 'monitor';\n"
        f"- User: 'Total customers?' → select count(distinct customer_name) as total_customers from sales;\n"
        f"- User: 'Total sales table?' → select sum(revenue) as total_sales from sales;\n"
        f"- User: 'Product and revenue?' → select distinct s.customer_name, s.revenue, o.product from sales s join orders o on s.customer_name = o.customer_name;\n"
    )

    url = "https://api.together.xyz/inference"  # Added the missing URL

    # API payload with your original parameters, adjusted for determinism if needed
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "prompt": f"<s>[INST] {prompt} [/INST>",
        "max_tokens": 512,  # Kept your original, but can increase to 1024 for complex queries
        "stop": ["</s>", "[/INST]"],
        "temperature": 0.7,  # Kept your original, but can lower to 0.05 for stricter adherence
        "top_p": 0.7,       # Kept your original, but can lower to 0.05 for focused responses
        "top_k": 50,        # Kept your original, but can reduce to 10 for consistency
        "repetition_penalty": 1,  # Kept your original, but can increase to 2.0 to avoid deviations
        "n": 1
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer API KEY"
    }

    # Make the API call
    response = requests.post(url, json=payload, headers=headers)

    # Process the response
    if response.status_code == 200:
        result = response.json()
        print("Full API Response:", result)  # Print the full response for debugging
        choices = result.get("output", {}).get("choices", [])
        if choices:
            raw_query = choices[0].get("text", "").strip()
            cleaned_query = clean_sql_query(raw_query)
            print("Generated SQL Query:", cleaned_query)

            # Determine the table(s) based on the query
            if "join" in cleaned_query.lower():
                # Handle queries spanning both tables (e.g., "product and revenue" or product-based with revenue)
                query_result = execute_query(cleaned_query, "sales")  # Use sales as the primary table for joins
            else:
                # Determine the table based on the query
                table_used = "sales" if any(t in cleaned_query.lower() for t in ["sales", "revenue", "region", "sale"]) else "orders"
                query_result = execute_query(cleaned_query, table_used)
            
            if "error" in query_result:
                print(f"Error: {query_result['error']}")
            else:
                print("Results:")
                print("Columns:", ", ".join(query_result["columns"]))
                for row in query_result["data"]:
                    print(row)
        else:
            print("No choices found in the response.")
    else:
        print(f"Error: {response.status_code}\n{response.text}")

def main():
    while True:
        user_query = input("Enter your query (e.g., 'top 3 customers by revenue') or 'quit' to exit: ").strip()
        if user_query.lower() == 'quit':
            print("Exiting...")
            break

        generate_and_execute_sql(user_query)
        print("\n" + "-"*50)

if __name__ == "__main__":
    main()