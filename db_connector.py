import pyodbc

server = "HP"
database = "AdventureWorks2019"
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Trusted_Connection=yes;"
)

def get_connection():
    return pyodbc.connect(conn_str)

def fetch_table(cursor, query, source_name):
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f"Raw rows fetched from {source_name}: {len(rows)}")  # debug print

    formatted = []
    for row in rows:
        if source_name == "HumanResources.Department":
            # row = (DepartmentID, Name, GroupName)
            text = f"DepartmentID: {row.DepartmentID}, Name: {row.Name}, Group: {row.GroupName}"
        elif source_name == "HumanResources.Employee":
            # row = (BusinessEntityID, JobTitle, BirthDate, Gender, HireDate)
            text = (
                f"EmployeeID: {row.BusinessEntityID}, "
                f"JobTitle: {row.JobTitle}, "
                f"BirthDate: {row.BirthDate}, "
                f"Gender: {row.Gender}, "
                f"HireDate: {row.HireDate}"
            )
        else:
            # fallback for other tables
            text = " ".join(str(value) for value in row)

        formatted.append({"text": text, "source": source_name})

    return formatted

def get_texts():
    conn = get_connection()
    cursor = conn.cursor()

    texts = []

    # --- Table 1: HumanResources.Employee ---
    texts.extend(fetch_table(
        cursor,
        "SELECT TOP 10 BusinessEntityID, JobTitle, BirthDate, Gender, HireDate FROM HumanResources.Employee",
        "HumanResources.Employee"
    ))

    # --- Table 2: HumanResources.Department ---
    texts.extend(fetch_table(
        cursor,
        "SELECT TOP 10 DepartmentID, Name, GroupName FROM HumanResources.Department",
        "HumanResources.Department"
    ))

    return texts

if __name__ == "__main__":
    texts = get_texts()
    print("Fetched rows:", len(texts))
    for t in texts:
        print(t)
