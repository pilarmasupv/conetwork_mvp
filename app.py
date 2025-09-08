from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)

# --- Load dataset ---
with open("graph_dataset.json", "r", encoding="utf-8") as f:
    graph_data = json.load(f)

nodes = graph_data.get("nodes", [])
edges = graph_data.get("edges", [])

# --- Home ---
@app.route("/")
def home():
    return render_template("index.html")

# --- Full graph data ---
@app.route("/api/graph")
def get_graph():
    # Optional filters
    country = request.args.get("country")
    subfield = request.args.get("subfield")
    min_year = request.args.get("year", type=int)

    filtered_nodes = nodes
    filtered_edges = edges

    if country and country != "all":
        filtered_nodes = [n for n in nodes if n.get("country") == country]
        allowed_ids = {n["id"] for n in filtered_nodes}
        filtered_edges = [e for e in edges if e["source"] in allowed_ids and e["target"] in allowed_ids]

    if subfield and subfield != "all":
        filtered_edges = [e for e in filtered_edges if e.get("subfield") == subfield]
        allowed_ids = {e["source"] for e in filtered_edges} | {e["target"] for e in filtered_edges}
        filtered_nodes = [n for n in filtered_nodes if n["id"] in allowed_ids]

    if min_year:
        filtered_edges = [e for e in filtered_edges if e.get("year", 0) >= min_year]
        allowed_ids = {e["source"] for e in filtered_edges} | {e["target"] for e in filtered_edges}
        filtered_nodes = [n for n in filtered_nodes if n["id"] in allowed_ids]

    return jsonify({"nodes": filtered_nodes, "edges": filtered_edges})

# --- Filters API ---
@app.route("/api/filters")
def get_filters():
    countries = sorted({n.get("country", "Unknown") for n in nodes})
    subfields = sorted({e.get("subfield", "Unknown") for e in edges})
    years = sorted({e.get("year", 0) for e in edges if "year" in e})

    return jsonify({
        "countries": countries,
        "subfields": subfields,
        "years": {"min": min(years) if years else None, "max": max(years) if years else None}
    })

# --- Author search ---
@app.route("/api/search")
def search_author():
    query = request.args.get("author", "").lower()
    if not query:
        return jsonify([])

    results = [n for n in nodes if query in n["id"].lower()]
    return jsonify(results[:10])  # top 10 matches

# --- Error handling ---
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error"}), 500

# --- Run app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
