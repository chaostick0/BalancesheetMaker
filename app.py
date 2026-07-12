import csv
import sqlite3
from io import StringIO
from flask import Flask, Response, redirect, render_template, request, flash, jsonify
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
    company = get_company()
    rows = get_balance_sheet_rows(section="ASSETS")
    group_names = sorted({row["group_name"] for row in rows if row.get("group_name")})
    return render_template("assets.html", assets=rows, company=company, group_names=group_names, group_totals=[])


@app.route("/add-asset", methods=["POST"])
def add_asset():
    section = "ASSETS"
    group_name_select = request.form.get("group_name_select", "").strip()
    if group_name_select == "__new__":
        group_name = (request.form.get("group_name", "").strip() or "Custom Group").strip()
    else:
        group_name = group_name_select or (request.form.get("group_name", "").strip() or "Custom Group")
    item_name = request.form.get("item_name", "").strip()
    note_no = request.form.get("note_no", "").strip() or ""
    if not item_name:
        message = "Please enter an asset name."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "error": message}), 400
        flash(message, "danger")
        return redirect("/assets")
    row_id = insert_balance_sheet_row(section, group_name, item_name, note_no)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"ok": True, "row_id": row_id, "group_name": group_name, "item_name": item_name, "note_no": note_no})
    flash("Asset row added successfully.", "success")
    return redirect("/assets")


@app.route("/remove-asset/<int:item_id>", methods=["POST"])
def remove_asset(item_id):
    if delete_balance_sheet_row(item_id):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": True})
        flash("Asset row removed successfully.", "success")
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "error": "Unable to remove that asset row."}), 400
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
    company = get_company()
    rows = get_balance_sheet_rows(section="LIABILITIES")
    group_names = sorted({row["group_name"] for row in rows if row.get("group_name")})
    return render_template("liabilities.html", liabilities=rows, company=company, group_names=group_names)


@app.route("/add-liability", methods=["POST"])
def add_liability():
    section = "LIABILITIES"
    group_name_select = request.form.get("group_name_select", "").strip()
    if group_name_select == "__new__":
        group_name = (request.form.get("group_name", "").strip() or "Custom Group").strip()
    else:
        group_name = group_name_select or (request.form.get("group_name", "").strip() or "Custom Group")
    item_name = request.form.get("item_name", "").strip()
    note_no = request.form.get("note_no", "").strip() or ""
    if not item_name:
        message = "Please enter a liability name."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "error": message}), 400
        flash(message, "danger")
        return redirect("/liabilities")
    row_id = insert_balance_sheet_row(section, group_name, item_name, note_no)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"ok": True, "row_id": row_id, "group_name": group_name, "item_name": item_name, "note_no": note_no})
    flash("Liability row added successfully.", "success")
    return redirect("/liabilities")


@app.route("/remove-liability/<int:item_id>", methods=["POST"])
def remove_liability(item_id):
    if delete_balance_sheet_row(item_id):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": True})
        flash("Liability row removed successfully.", "success")
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"ok": False, "error": "Unable to remove that liability row."}), 400
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
    return render_template("export.html", company=get_company())


@app.route("/import/csv", methods=["POST"])
def import_csv():
    uploaded = request.files.get("csv_file")
    if not uploaded or not uploaded.filename:
        flash("Please choose a CSV file to import.", "danger")
        return redirect("/export")

    try:
        csv_text = uploaded.read().decode("utf-8")
        replace_existing = request.form.get("replace_existing") == "on"
        imported_count = import_balance_sheet_from_csv(csv_text, replace_existing=replace_existing)
        flash(f"Imported {imported_count} balance sheet rows successfully.", "success")
    except Exception as exc:
        flash(f"Import failed: {exc}", "danger")
    return redirect("/export")


@app.route("/export/csv")
def export_csv():
    company = get_company() or {}
    rows = get_balance_sheet_rows()
    sample = request.args.get("sample") == "1"

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["Company Name", company.get("company_name", "")])
    writer.writerow(["Balance Sheet Date", company.get("balance_sheet_date", "")])
    writer.writerow(["Currency", company.get("currency", "")])
    writer.writerow(["Current Year", company.get("current_year", "")])
    writer.writerow(["Previous Year", company.get("previous_year", "")])
    writer.writerow([])
    writer.writerow(["Section", "Group", "Particular", "Note", "Current Amount", "Previous Amount"])
    if sample:
        writer.writerow(["ASSETS", "Current Assets", "Cash", "1", "100", "80"])
    else:
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
    total_assets = get_balance_sheet_totals("ASSETS")["current_amount"]
    total_liabilities = get_balance_sheet_totals("LIABILITIES")["current_amount"]

    def escape_pdf_text(text):
        return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    stream_parts = []

    def add_text(x, y, text, size=11):
        escaped_text = escape_pdf_text(text)
        stream_parts.append(f"BT /F1 {size} Tf {x} {y} Td ({escaped_text}) Tj ET")

    def add_line(x1, y1, x2, y2):
        stream_parts.append(f"{x1} {y1} m {x2} {y2} l S")

    add_text(72, 760, "Balance Sheet Report", 16)
    add_text(72, 740, f"Company: {company.get('company_name', '')}", 11)
    add_text(72, 724, f"Date: {company.get('balance_sheet_date', '')}", 11)
    add_line(72, 710, 540, 710)

    add_text(72, 690, "Assets", 13)
    add_line(72, 678, 540, 678)
    y_position = 660
    for row in assets:
        add_text(84, y_position, f"- {row['item_name']} ({row['group_name']})", 10)
        add_text(440, y_position, f"{row['current_amount']:.2f}", 10)
        y_position -= 14
    add_text(72, y_position - 12, f"Total Assets: {total_assets:.2f}", 11)
    add_line(72, y_position - 24, 540, y_position - 24)

    y_position -= 36
    add_text(72, y_position, "Liabilities", 13)
    add_line(72, y_position - 12, 540, y_position - 12)
    y_position -= 30
    for row in liabilities:
        add_text(84, y_position, f"- {row['item_name']} ({row['group_name']})", 10)
        add_text(440, y_position, f"{row['current_amount']:.2f}", 10)
        y_position -= 14
    add_text(72, y_position - 12, f"Total Liabilities: {total_liabilities:.2f}", 11)

    stream_content = "\n".join(stream_parts)
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
