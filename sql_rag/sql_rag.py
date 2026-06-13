"""SQL RAG: text-to-SQL over mediassist.db using Groq + LangChain SQLDatabase."""

import re
import sqlite3
from pathlib import Path

from groq import Groq

DB_PATH = Path(__file__).resolve().parent.parent / "data/db/mediassist.db"
GROQ_MODEL = "llama-3.3-70b-versatile"
SQL_RAG_ROLES = {"billing_executive", "admin"}
SAMPLE_ROWS = 2
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolve_db_path(db_path: str | Path) -> Path:
    path = Path(db_path).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()

# Function to read the table structures from the database
def read_table_structures(db_path: str | Path = DB_PATH) -> str:
    path = _resolve_db_path(db_path)
    if not path.exists():
        raise FileNotFoundError(f"Database file not found: {path}")

    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT type, name FROM sqlite_master ORDER BY type, name")
        objects = cursor.fetchall()

        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        if not tables:
            objects_list = ", ".join(f"{t}:{n}" for t, n in objects) or "none"
            raise ValueError(
                f"No tables found in database: {path} "
                f"({path.stat().st_size} bytes). "
                f"sqlite_master objects: {objects_list}"
            )

        parts = []
        for name in tables:
            cursor.execute(f'PRAGMA table_info("{name}")')
            columns = cursor.fetchall()
            col_defs = ", ".join(
                f"{col[1]} {col[2]}" + (" PRIMARY KEY" if col[5] else "")
                for col in columns
            )
            parts.append(f"Table {name}: {col_defs}")

            cursor.execute(f'SELECT * FROM "{name}" LIMIT {SAMPLE_ROWS}')
            rows = cursor.fetchall()
            if rows:
                parts.append(f"-- Sample rows from {name}: {rows}")

        return "\n\n".join(parts)
    finally:
        conn.close()

# Function to clean the SQL query
def clean_sql(raw: str) -> str:
    sql = raw.strip()
    match = re.search(r"```(?:sql)?\s*(.*?)```", sql, re.DOTALL | re.IGNORECASE)
    if match:
        sql = match.group(1).strip()
    sql = re.sub(r"^SQLQuery:\s*", "", sql, flags=re.IGNORECASE).strip().rstrip(";")
    if not sql.upper().lstrip().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")
    if "LIMIT" not in sql.upper() and not re.search(
        r"\b(COUNT|SUM|AVG|MIN|MAX)\s*\(", sql, re.IGNORECASE
    ):
        sql = f"{sql} LIMIT 50"
    return sql

# Function to run the SQL query and return the results
def run_sql(sql: str, db_path: str | Path = DB_PATH) -> str:
    path = _resolve_db_path(db_path)
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        if not rows:
            return "No rows."
        lines = [", ".join(columns)]
        for row in rows:
            lines.append(", ".join(str(value) for value in row))
        return "\n".join(lines)
    finally:
        conn.close()

# Function to answer the user's question using the SQL RAG
def sql_rag_answer(question: str) -> dict:
    client = Groq()
    schema = read_table_structures(DB_PATH)

    raw_sql = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You write SQLite SELECT queries. Return only the SQL query.\n"
                    "For how many/count/total questions, use COUNT(*).\n"
                    "For sum/average questions, use SUM() or AVG().\n\n"
                    f"Schema:\n{schema}"
                ),
            },
            {"role": "user", "content": question},
        ],
        temperature=0,
    ).choices[0].message.content

    sql = clean_sql(raw_sql)
    results = run_sql(sql)
    answer = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer using only the SQL results. Be precise and short: "
                    "one or two sentences maximum. State the key number or "
                    "finding directly. Do not explain departments, medical "
                    "context, or what the result might imply."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\nSQL: {sql}\nResults:\n{results}"
                ),
            },
        ],
        temperature=0,
    ).choices[0].message.content

    return {"answer": answer, "sql": sql, "results": results}


def sql_rag_chain(question: str) -> str:
    return sql_rag_answer(question)["answer"]


if __name__ == "__main__":
    import sys

    question = sys.argv[1] if len(sys.argv) > 1 else "How many claims are pending?"
    print(sql_rag_chain(question))
