import sqlite3
from flask import Flask, render_template, request, send_file, redirect, url_for
from io import BytesIO
from reportlab.pdfgen import canvas
from database import save_invoice, get_invoices, get_summary, delete_invoice, search_invoices, get_invoice_items

app = Flask(__name__, template_folder=r"C:\Users\israt\OneDrive\Desktop\InvoiceGenerator\templates")


@app.route("/")
def home():
    summary = get_summary()
    return render_template("index.html", summary=summary)


@app.route("/download", methods=["POST"])

def download():
    customer = request.form.get("customer", "").strip()
    products = request.form.getlist("product[]")
    quantities = request.form.getlist("quantity[]")
    prices = request.form.getlist("price[]")

    if not customer or not products:
        return "Please enter customer and product details.", 400

    if not (len(products) == len(quantities) == len(prices)):
        return "Invalid product details.", 400

    items = []
    grand_total = 0

    try:
        for product, quantity, price in zip(products, quantities, prices):
            product = product.strip()
            quantity = int(quantity)
            price = float(price)

            if not product or quantity <= 0 or price <= 0:
                return "Please enter valid product details.", 400

            subtotal = quantity * price
            items.append({
                "product": product,
                "quantity": quantity,
                "price": price,
                "subtotal": subtotal
            })
            grand_total += subtotal

    except ValueError:
        return "Please enter valid quantities and prices.", 400

    invoice_id = save_invoice(
        customer,
        items[0]["product"],
        sum(item["quantity"] for item in items),
        0,
        grand_total
    )

    connection = sqlite3.connect("invoices.db")

    for item in items:
        connection.execute("""
            INSERT INTO invoice_items
            (invoice_id, product, quantity, price, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (
            invoice_id,
            item["product"],
            item["quantity"],
            item["price"],
            item["subtotal"]
        ))

    connection.commit()
    connection.close()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(595, 842))
    pdf.setTitle("Invoice")

    pdf.setFillColorRGB(0.12, 0.23, 0.40)
    pdf.rect(0, 740, 595, 102, fill=1, stroke=0)

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(40, 790, "INVOICE")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, 765, "Invoice No: INV-%04d" % invoice_id)

    pdf.setFillColorRGB(0.15, 0.20, 0.28)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, 705, "Customer: " + customer[:50])

    pdf.setFillColorRGB(0.12, 0.23, 0.40)
    pdf.rect(40, 650, 515, 30, fill=1, stroke=0)

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(48, 661, "PRODUCT")
    pdf.drawString(280, 661, "QTY")
    pdf.drawString(350, 661, "PRICE")
    pdf.drawString(450, 661, "AMOUNT")

    y = 625
    pdf.setFillColorRGB(0.15, 0.20, 0.28)
    pdf.setFont("Helvetica", 10)

    for item in items:
        if y < 100:
            pdf.showPage()
            y = 780
            pdf.setFillColorRGB(0.15, 0.20, 0.28)
            pdf.setFont("Helvetica", 10)

        pdf.drawString(48, y, item["product"][:32])
        pdf.drawString(285, y, str(item["quantity"]))
        pdf.drawString(350, y, "Rs. %.2f" % item["price"])
        pdf.drawString(450, y, "Rs. %.2f" % item["subtotal"])
        y -= 28

    y -= 15
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawRightString(550, y, "Grand Total: Rs. %.2f" % grand_total)

    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(297, 55, "Thank you for your business!")

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="invoice_%04d.pdf" % invoice_id,
        mimetype="application/pdf"
    )


    # Save invoice details in the database
    invoice_id = save_invoice(customer, product, quantity, price, total)

    # Create PDF invoice
    buffer = BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=(595, 842))
    pdf.setTitle("Professional Invoice")

    # Header background
    pdf.setFillColorRGB(0.47, 0.33, 0.26)
    pdf.rect(0, 740, 595, 102, fill=1, stroke=0)

    # Company heading
    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 25)
    pdf.drawString(40, 790, "INVOICE")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, 765, "BILLING & PAYMENT DETAILS")

    # Invoice information
    pdf.setFillColorRGB(0.15, 0.20, 0.28)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(40, 700, "BILL TO")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, 675, f"Customer: {customer}")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(400, 700, "INVOICE NO.")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(400, 675, f"INV-{invoice_id:04d}")

    # Product table heading
    pdf.setFillColorRGB(0.12, 0.23, 0.40)
    pdf.rect(40, 610, 515, 35, fill=1, stroke=0)

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(52, 622, "PRODUCT")
    pdf.drawString(285, 622, "QTY")
    pdf.drawString(355, 622, "PRICE")
    pdf.drawString(455, 622, "AMOUNT")

    # Product row
    pdf.setFillColorRGB(0.15, 0.20, 0.28)
    pdf.setFont("Helvetica", 11)
    pdf.drawString(52, 585, product[:30])
    pdf.drawString(290, 585, str(quantity))
    pdf.drawString(355, 585, f"Rs. {price:.2f}")
    pdf.drawString(455, 585, f"Rs. {total:.2f}")

    pdf.setStrokeColorRGB(0.82, 0.85, 0.90)
    pdf.line(40, 565, 555, 565)

    # Total box
    pdf.setFillColorRGB(0.91, 0.96, 0.93)
    pdf.roundRect(330, 490, 225, 55, 8, fill=1, stroke=0)

    pdf.setFillColorRGB(0.08, 0.35, 0.20)
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(350, 510, f"TOTAL: Rs. {total:.2f}")

    # Footer
    pdf.setFillColorRGB(0.35, 0.39, 0.45)
    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(297, 100, "Thank you for your business!")
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(297, 80, "Generated using Invoice Generator")

    pdf.save()


    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="invoice.pdf",
        mimetype="application/pdf"
    )


@app.route("/history")
def history():
    invoices = get_invoices()
    invoice_list = []

    for invoice in invoices:
        invoice_data = dict(invoice)
        invoice_data["items"] = get_invoice_items(invoice["id"])
        invoice_list.append(invoice_data)

    return render_template("history.html", invoices=invoice_list)

@app.route("/delete/<int:invoice_id>", methods=["POST"])
def delete(invoice_id):
    delete_invoice(invoice_id)
    return redirect(url_for("history"))


@app.route("/search")
def search():
    customer_name = request.args.get("customer", "").strip()
    invoices = search_invoices(customer_name)

    invoice_list = []
    for invoice in invoices:
        invoice_data = dict(invoice)
        invoice_data["items"] = get_invoice_items(invoice["id"])
        invoice_list.append(invoice_data)

    return render_template(
        "history.html",
        invoices=invoice_list,
        search_query=customer_name
    )


if __name__ == "__main__":
    app.run(debug=True)