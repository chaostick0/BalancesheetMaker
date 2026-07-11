import csv
import sqlite3
from io import StringIO
from flask import Flask, Response, redirect, render_template, request, flash
from database import (
    delete_balance_sheet_row,
    get_balance_sheet_rows,
    get_balance_sheet_totals,
    get_company,
    import_balance_sheet_from_csv,
    initialize_database,
    insert_balance_sheet_row,
    normalize_amount,
    round_amount,
    save_balance_sheet_values,
    upsert_company,
)

app = Flask(__name__)
app.secret_key = "balancesheet-maker-secret"

initialize_database()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


@app.route("/")
def dashboard():
    company = get_company()
    assets_totals = get_balance_sheet_totals("ASSETS")
    liabilities_totals = get_balance_sheet_totals("LIABILITIES")

    assets_current = assets_totals["current_amount"]
    assets_previous = assets_totals["previous_amount"]
    liabilities_current = liabilities_totals["current_amount"]
    liabilities_previous = liabilities_totals["previous_amount"]

    current_difference = round_amount(assets_current - liabilities_current)
    previous_difference = round_amount(assets_previous - liabilities_previous)
    balanced = abs(current_difference) < 0.01 and abs(previous_difference) < 0.01
    status_message = "Balanced" if balanced else f"Difference: ₹ {current_difference:,.2f}"

    trend_message = "Improving" if current_difference <= 0 else "Needs review"
    if not balanced:
        trend_message = "Drifting" if abs(current_difference) > 10000 else "Needs review"

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
        status_message=status_message,
        trend_message=trend_message,
    )


@app.route("/company")
def company():
    company = get_company()
    return render_template("company.html", company=company)


@app.route("/save-company", methods=["POST"])
def save_company():
    data = {
        "company_name": request.form.get("company_name", ""),
        "balance_sheet_date": request.form.get("balance_sheet_date", ""),
        "currency": request.form.get("currency", ""),
        "current_year": request.form.get("current_year", ""),
        "previous_year": request.form.get("previous_year", ""),
    }
    try:
        upsert_company(data)
        flash("Company details saved successfully.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect("/company")


@app.route("/assets")
def assets():
    rows = get_balance_sheet_rows(section="ASSETS")
    return render_template("assets.html", assets=rows, group_totals=[])


@app.route("/add-asset", methods=["POST"])
def add_asset():
    section = "ASSETS"
    group_name = request.form.get("group_name", "Custom Group").strip() or "Custom Group"
    item_name = request.form.get("item_name", "").strip()
    note_no = request.form.get("note_no", "").strip() or ""
    if not item_name:
        flash("Please enter an asset name.", "danger")
        return redirect("/assets")
    insert_balance_sheet_row(section, group_name, item_name, note_no)
    flash("Asset row added successfully.", "success")
    return redirect("/assets")


@app.route("/remove-asset/<int:item_id>", methods=["POST"])
def remove_asset(item_id):
    if delete_balance_sheet_row(item_id):
        flash("Asset row removed successfully.", "success")
    else:
        flash("Unable to remove that asset row.", "danger")
    return redirect("/assets")


@app.route("/save-assets", methods=["POST"])
def save_assets():
    payload = {}
    for key, value in request.form.items():
        if key.startswith("current_"):
            item_id = key.split("_", 1)[1]
            payload.setdefault(item_id, {})["current_amount"] = value
        elif key.startswith("previous_"):
            item_id = key.split("_", 1)[1]
            payload.setdefault(item_id, {})["previous_amount"] = value

    try:
        save_balance_sheet_values("ASSETS", payload)
        flash("Assets updated successfully.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect("/assets")


@app.route("/liabilities")
def liabilities():
    rows = get_balance_sheet_rows(section="LIABILITIES")
    return render_template("liabilities.html", liabilities=rows)


@app.route("/add-liability", methods=["POST"])
def add_liability():
    section = "LIABILITIES"
    group_name = request.form.get("group_name", "Custom Group").strip() or "Custom Group"
    item_name = request.form.get("item_name", "").strip()
    note_no = request.form.get("note_no", "").strip() or ""
    if not item_name:
        flash("Please enter a liability name.", "danger")
        return redirect("/liabilities")
    insert_balance_sheet_row(section, group_name, item_name, note_no)
    flash("Liability row added successfully.", "success")
    return redirect("/liabilities")


@app.route("/remove-liability/<int:item_id>", methods=["POST"])
def remove_liability(item_id):
    if delete_balance_sheet_row(item_id):
        flash("Liability row removed successfully.", "success")
    else:
        flash("Unable to remove that liability row.", "danger")
    return redirect("/liabilities")


@app.route("/save-liabilities", methods=["POST"])
def save_liabilities():
    payload = {}
    for key, value in request.form.items():
        if key.startswith("current_"):
            item_id = key.split("_", 1)[1]
            payload.setdefault(item_id, {})["current_amount"] = value
        elif key.startswith("previous_"):
            item_id = key.split("_", 1)[1]
            payload.setdefault(item_id, {})["previous_amount"] = value

    try:
        save_balance_sheet_values("LIABILITIES", payload)
        flash("Liabilities updated successfully.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect("/liabilities")


@app.route("/report")
def report():
    company = get_company()
    assets = get_balance_sheet_rows(section="ASSETS")
    liabilities = get_balance_sheet_rows(section="LIABILITIES")
    total_assets = get_balance_sheet_totals("ASSETS")["current_amount"]
    total_liabilities = get_balance_sheet_totals("LIABILITIES")["current_amount"]

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


@app.route("/import/csv", methods=["POST"])
def import_csv():
    uploaded = request.files.get("csv_file")
    if not uploaded or not uploaded.filename:
        flash("Please choose a CSV file to import.", "danger")
        return redirect("/export")

    try:
        csv_text = uploaded.read().decode("utf-8")
        imported_count = import_balance_sheet_from_csv(csv_text)
        flash(f"Imported {imported_count} balance sheet rows successfully.", "success")
    except Exception as exc:
        flash(f"Import failed: {exc}", "danger")
    return redirect("/export")


@app.route("/export/csv")
def export_csv():
    company = get_company() or {}
    rows = get_balance_sheet_rows()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["Company Name", company.get("company_name", "")])
    writer.writerow(["Balance Sheet Date", company.get("balance_sheet_date", "")])
    writer.writerow(["Currency", company.get("currency", "")])
    writer.writerow(["Current Year", company.get("current_year", "")])
    writer.writerow(["Previous Year", company.get("previous_year", "")])
    writer.writerow([])
    writer.writerow(["Section", "Group", "Particular", "Note", "Current Amount", "Previous Amount"])
    writer.writerows(
        [
            [
                row["section"],
                row["group_name"],
                row["item_name"],
                row["note_no"],
                row["current_amount"],
                row["previous_amount"],
            ]
            for row in rows
        ]
    )

    csv_data = output.getvalue()
    response = Response(csv_data, mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=balance_sheet_export.csv"
    return response


@app.route("/export/pdf")
def export_pdf():
    company = get_company() or {}
    assets = get_balance_sheet_rows(section="ASSETS")
    liabilities = get_balance_sheet_rows(section="LIABILITIES")

    body = [
        f"Balance Sheet Report",
        f"Company: {company.get('company_name', '')}",
        f"Date: {company.get('balance_sheet_date', '')}",
        "",
        "Assets",
    ]
    for row in assets:
        body.append(f"- {row['item_name']}: {row['current_amount']}")
    body.extend(["", "Liabilities"])
    for row in liabilities:
        body.append(f"- {row['item_name']}: {row['current_amount']}")

    response = Response("\n".join(body), mimetype="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=balance_sheet_export.pdf"
    return response


if __name__ == "__main__":
    app.run(debug=True)
