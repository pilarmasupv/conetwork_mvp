from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

# Load graph dataset
with open("graph_dataset.json", "r", encoding="utf-8") as f:
    graph_data = json.load(f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/graph")
def get_graph():
    return jsonify(graph_data)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
