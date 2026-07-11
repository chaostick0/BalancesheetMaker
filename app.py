import csv
import sqlite3
from io import StringIO
from flask import Flask, Response, render_template, request, redirect
from database import initialize_database

app = Flask(__name__)

initialize_database()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


@app.route("/")
def dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM company LIMIT 1")
    company = cursor.fetchone()

    cursor.execute("""
        SELECT SUM(current_amount), SUM(previous_amount)
        FROM balance_sheet
        WHERE section='ASSETS'
    """)
    asset_totals = cursor.fetchone()

    cursor.execute("""
        SELECT SUM(current_amount), SUM(previous_amount)
        FROM balance_sheet
        WHERE section IN ('EQUITY AND LIABILITIES', 'LIABILITIES')
    """)
    liability_totals = cursor.fetchone()

    conn.close()

    assets_current = (asset_totals[0] if asset_totals and asset_totals[0] is not None else 0)
    assets_previous = (asset_totals[1] if asset_totals and asset_totals[1] is not None else 0)

    liabilities_current = (liability_totals[0] if liability_totals and liability_totals[0] is not None else 0)
    liabilities_previous = (liability_totals[1] if liability_totals and liability_totals[1] is not None else 0)

    current_difference = assets_current - liabilities_current
    previous_difference = assets_previous - liabilities_previous

    balanced = (
    abs(current_difference) < 0.01 and
    abs(previous_difference) < 0.01
    )
    status_message = (
    "Balanced"
    if balanced
    else f"Difference: ₹ {current_difference:,.2f}"
    )

    return render_template(
        "dashboard.html",
        company=company,
        assets_current=assets_current,
        assets_previous=assets_previous,
        liabilities_current=liabilities_current,
        liabilities_previous=liabilities_previous,
        current_difference=current_difference,
        previous_difference=previous_difference,
        balanced=balanced,
        status_message=status_message
    )


@app.route("/company")
def company():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM company LIMIT 1")
    company = cursor.fetchone()
    conn.close()
    return render_template("company.html", company=company)


@app.route("/save-company", methods=["POST"])
def save_company():
    company_name = request.form["company_name"]
    balance_sheet_date = request.form["balance_sheet_date"]
    currency = request.form["currency"]
    current_year = request.form["current_year"]
    previous_year = request.form["previous_year"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM company")
    cursor.execute("""
        INSERT INTO company(
            company_name,balance_sheet_date,currency,current_year,previous_year
        ) VALUES (?,?,?,?,?)
    """, (company_name,balance_sheet_date,currency,current_year,previous_year))
    conn.commit()
    conn.close()
    return redirect("/company")


@app.route("/assets")
def assets():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            group_name,
            item_name,
            note_no,
            current_amount,
            previous_amount
        FROM balance_sheet
        WHERE section='ASSETS'
        ORDER BY group_name, note_no
    """)

    assets = cursor.fetchall()

    cursor.execute("""
        SELECT
            group_name,
            SUM(current_amount),
            SUM(previous_amount)
        FROM balance_sheet
        WHERE section='ASSETS'
        GROUP BY group_name
    """)

    group_totals = cursor.fetchall()

    conn.close()

    return render_template(
        "assets.html",
        assets=assets,
        group_totals=group_totals
    )


@app.route("/save-assets", methods=["POST"])
def save_assets():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM balance_sheet WHERE section='ASSETS'")
    for (item_id,) in cursor.fetchall():
        current = request.form.get(f"current_{item_id}", 0)
        previous = request.form.get(f"previous_{item_id}", 0)
        cursor.execute(
            "UPDATE balance_sheet SET current_amount=?, previous_amount=? WHERE id=?",
            (current, previous, item_id),
        )
    conn.commit()
    conn.close()
    return redirect("/assets")


@app.route("/liabilities")
def liabilities():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM balance_sheet
        WHERE section IN ('EQUITY AND LIABILITIES', 'LIABILITIES')
        ORDER BY group_name,note_no
    """)
    liabilities = cursor.fetchall()
    conn.close()
    return render_template("liabilities.html", liabilities=liabilities)


@app.route("/save-liabilities", methods=["POST"])
def save_liabilities():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM balance_sheet WHERE section IN ('EQUITY AND LIABILITIES', 'LIABILITIES')")
    for (item_id,) in cursor.fetchall():
        current = request.form.get(f"current_{item_id}", 0)
        previous = request.form.get(f"previous_{item_id}", 0)
        cursor.execute(
            "UPDATE balance_sheet SET current_amount=?, previous_amount=? WHERE id=?",
            (current, previous, item_id),
        )
    conn.commit()
    conn.close()
    return redirect("/liabilities")


@app.route("/report")
def report():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM company LIMIT 1")
    company = cursor.fetchone()

    cursor.execute("SELECT * FROM balance_sheet WHERE section='ASSETS' ORDER BY group_name,note_no")
    assets = cursor.fetchall()

    cursor.execute("SELECT * FROM balance_sheet WHERE section IN ('EQUITY AND LIABILITIES', 'LIABILITIES') ORDER BY group_name,note_no")
    liabilities = cursor.fetchall()

    cursor.execute("SELECT SUM(current_amount) FROM balance_sheet WHERE section='ASSETS'")
    total_assets = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(current_amount) FROM balance_sheet WHERE section IN ('EQUITY AND LIABILITIES', 'LIABILITIES')")
    total_liabilities = cursor.fetchone()[0] or 0

    conn.close()

    return render_template(
        "report.html",
        company=company,
        assets=assets,
        liabilities=liabilities,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
    )


@app.route("/export")
def export():
    return render_template("export.html")


@app.route("/export/csv")
def export_csv():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM company LIMIT 1")
    company = cursor.fetchone()
    cursor.execute(
        "SELECT section, group_name, item_name, note_no, current_amount, previous_amount FROM balance_sheet ORDER BY section, group_name, note_no"
    )
    rows = cursor.fetchall()
    conn.close()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["Company Name", company[1] if company else ""])
    writer.writerow(["Balance Sheet Date", company[2] if company else ""])
    writer.writerow(["Currency", company[3] if company else ""])
    writer.writerow(["Current Year", company[4] if company else ""])
    writer.writerow(["Previous Year", company[5] if company else ""])
    writer.writerow([])
    writer.writerow(["Section", "Group", "Particular", "Note", "Current Amount", "Previous Amount"])
    writer.writerows(rows)

    csv_data = output.getvalue()
    response = Response(csv_data, mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=balance_sheet_export.csv"
    return response


if __name__ == "__main__":
    app.run(debug=True)
