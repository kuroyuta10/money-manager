from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)

DATA_FILE = "data.json"

# JSONファイルからデータを読み込む
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "current_money": 0,
            "transactions": [],
            "future_expenses": [],
            "notes": []
        }

# JSONファイルに保存する
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 起動時に読み込み
data = load_data()

@app.route("/", methods=["GET", "POST"])
def index():
    global data

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_money":
            val = request.form.get("current_money")
            if val and val.isdigit():
                data["current_money"] = int(val)

        elif action == "add_income":
            item = request.form.get("item")
            amount = request.form.get("amount")
            if item and amount and amount.isdigit():
                data["transactions"].append({
                    "item": item,
                    "amount": int(amount),
                    "type": "income"
                })
                data["current_money"] += int(amount)

        elif action == "add_expense":
            item = request.form.get("item")
            amount = request.form.get("amount")
            if item and amount and amount.isdigit():
                data["transactions"].append({
                    "item": item,
                    "amount": int(amount),
                    "type": "expense"
                })
                data["current_money"] -= int(amount)

        elif action == "delete_transaction":
            index = int(request.form.get("index"))
            transaction = data["transactions"][index]
            if transaction["type"] == "income":
                data["current_money"] -= transaction["amount"]
            else:
                data["current_money"] += transaction["amount"]
            del data["transactions"][index]

        elif action == "add_future":
            item = request.form.get("future_item")
            amount = request.form.get("future_amount")
            if item and amount and amount.isdigit():
                data["future_expenses"].append({
                    "item": item,
                    "amount": int(amount)
                })

        elif action == "add_note":
            note = request.form.get("note")
            if note:
                data["notes"].append(note)

        save_data(data)

    total_spent = sum([
        t["amount"] for t in data["transactions"]
        if t["type"] == "expense"
    ])

    return render_template(
        "index.html",
        data=data,
        total_spent=total_spent
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Renderが指定するポート番号を取得
    app.run(host="0.0.0.0", port=port)
