from flask import Flask, render_template, request, redirect, session, send_file, jsonify
from reportlab.pdfgen import canvas
import csv
import os
import random

app = Flask(__name__)
app.secret_key = "flight_secret_123"

BOOKINGS_FILE = "bookings.csv"

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- SEARCH ----------------
@app.route("/search", methods=["POST"])
def search():
    flights = []

    for i in range(3):  # generate multiple flights
        flights.append({
            "airline": random.choice(["FlightGuide Air", "SkyLine", "AeroJet"]),
            "from": request.form.get("from"),
            "to": request.form.get("to"),
            "class": random.choice(["Economy", "Business"]),
            "price": random.randint(800, 2500),
            "hotel": random.choice(["Hilton", "Marriott", "None"])
        })

    return render_template("index.html", flights=flights)

# ---------------- PAY ----------------
@app.route("/pay", methods=["POST"])
def pay():
    session["booking"] = request.form.to_dict()
    return render_template("payment.html", data=session["booking"])

# ---------------- CONFIRM PAYMENT ----------------
@app.route("/confirm_payment", methods=["POST"])
def confirm_payment():
    booking = session.get("booking")

    if not booking:
        return redirect("/")

    file_exists = os.path.isfile(BOOKINGS_FILE)

    with open(BOOKINGS_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["airline", "from", "to", "class", "hotel", "total"])

        writer.writerow([
            booking.get("airline", "FlightGuide Air"),
            booking.get("from", ""),
            booking.get("to", ""),
            booking.get("class", ""),
            booking.get("hotel", ""),
            booking.get("total", "")
        ])

    return redirect("/ticket")

# ---------------- TICKET ----------------
@app.route("/ticket")
def ticket():
    b = session.get("booking")

    if not b:
        return redirect("/")

    seat = str(random.randint(1, 30)) + random.choice(["A", "B", "C", "D"])
    gate = "G" + str(random.randint(1, 20))

    file_path = f"ticket_{random.randint(1000,9999)}.pdf"
    c = canvas.Canvas(file_path)

    # HEADER
    c.setFillColorRGB(1, 0.6, 0)
    c.rect(0, 780, 600, 50, fill=1)

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, 800, "FLIGHTGUIDE AIRLINES")

    # TITLE
    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, 740, "BOARDING PASS")

    # BOX
    c.rect(30, 520, 540, 200)

    # ROW 1
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 690, "PASSENGER")
    c.drawString(180, 690, "FROM")
    c.drawString(300, 690, "TO")
    c.drawString(420, 690, "CLASS")

    c.setFont("Helvetica", 11)
    c.drawString(50, 670, "Guest User")
    c.drawString(180, 670, b.get("from", "N/A"))
    c.drawString(300, 670, b.get("to", "N/A"))
    c.drawString(420, 670, b.get("class", "N/A"))

    # ROW 2
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 630, "AIRLINE")
    c.drawString(180, 630, "SEAT")
    c.drawString(300, 630, "GATE")
    c.drawString(420, 630, "PRICE")

    c.setFont("Helvetica", 11)
    c.drawString(50, 610, b.get("airline", "FlightGuide Air"))
    c.drawString(180, 610, seat)
    c.drawString(300, 610, gate)
    c.drawString(420, 610, str(b.get("total", "N/A")) + " AED")

    c.line(50, 560, 550, 560)

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(170, 540, "Have a safe flight ✈ FlightGuide")

    c.save()

    session.pop("booking", None)

    return send_file(file_path, as_attachment=True)

# ---------------- SMART CHATBOT ----------------
@app.route("/chatbot", methods=["POST"])
def chatbot():
    msg = request.json.get("message", "").lower()

    if any(word in msg for word in ["hi", "hello", "hey"]):
        reply = "✈ Hey! I'm FlightGuide Assistant. I can help you use the app and book flights."

    elif "how" in msg and ("use" in msg or "work" in msg):
        reply = "✈ Steps:\n1. Enter From & To\n2. Click Search\n3. Choose a flight\n4. Click Book\n5. Pay → Ticket downloads!"

    elif "search" in msg:
        reply = "✈ Enter your departure and destination at the top, then click Search."

    elif "book" in msg:
        reply = "✈ After searching, click the 'Book ✈' button on any flight."

    elif "payment" in msg or "pay" in msg:
        reply = "✈ Complete payment to generate your boarding pass."

    elif "ticket" in msg:
        reply = "✈ Your ticket downloads automatically after payment as a PDF."

    elif "price" in msg:
        reply = "✈ Prices vary by class. Economy is cheaper than Business."

    elif "hotel" in msg:
        reply = "✈ Some flights include hotel options like Hilton or Marriott."

    elif "class" in msg:
        reply = "✈ Economy is standard, Business offers more comfort."

    elif "error" in msg or "not working" in msg:
        reply = "✈ Try refreshing the page or searching again."

    else:
        reply = "✈ I can help with booking, payments, and tickets. Try asking 'How do I book?'"

    return jsonify({"reply": reply})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)