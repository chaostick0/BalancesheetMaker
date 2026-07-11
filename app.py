import csv
import sqlite3
from io import BytesIO, StringIO
from flask import Flask, Response, redirect, render_template, request, flash
from database import (
    delete_balance_sheet_row,
    get_balance_sheet_rows,
    get_balance_sheet_totals,
    get_company,
    get_dashboard_summary,
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
    summary = get_dashboard_summary()

    return render_template(
        "dashboard.html",
        company=company,
        assets_current=summary["assets_current"],
        assets_previous=summary["assets_previous"],
        liabilities_current=summary["liabilities_current"],
        liabilities_previous=summary["liabilities_previous"],
        current_difference=summary["current_difference"],
        previous_difference=summary["previous_difference"],
        balanced=summary["balanced"],
        status_message=summary["balance_status"],
        trend_message=summary["trend_message"],
        current_ratio=summary["current_ratio"],
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

    content_lines = [
        "Balance Sheet Report",
        f"Company: {company.get('company_name', '')}",
        f"Date: {company.get('balance_sheet_date', '')}",
        "",
        "Assets",
        *[f"- {row['item_name']}: {row['current_amount']}" for row in assets],
        "",
        "Liabilities",
        *[f"- {row['item_name']}: {row['current_amount']}" for row in liabilities],
    ]

    def escape_pdf_text(text):
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    stream_lines = []
    for index, line in enumerate(content_lines):
        y_position = 760 - (index * 14)
        escaped_line = escape_pdf_text(line)
        stream_lines.append(f"BT /F1 12 Tf 72 {y_position} Td ({escaped_line}) Tj ET")

    stream_content = "\n".join(stream_lines)
    stream_bytes = stream_content.encode("latin-1", "replace")

    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(stream_bytes)} >>\nstream\n{stream_content}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf_parts = [b"%PDF-1.4\n"]
    offsets = []
    for index, body in enumerate(objects, start=1):
        offsets.append(len(b"".join(pdf_parts)))
        pdf_parts.append(f"{index} 0 obj\n{body}\nendobj\n".encode("latin-1", "replace"))

    xref_offset = len(b"".join(pdf_parts))
    pdf_parts.append(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin-1"))
    for offset in offsets:
        pdf_parts.append(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf_parts.append(f"trailer<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin-1"))

    response = Response(b"".join(pdf_parts), mimetype="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=balance_sheet_export.pdf"
    return response


if __name__ == "__main__":
    app.run(debug=True)
