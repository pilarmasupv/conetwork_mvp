from flask import Flask, render_template, jsonify, request
import json, os

app = Flask(__name__)

# Load dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), "graph_dataset.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    graph_data = json.load(f)

nodes = graph_data.get("nodes", [])
edges = graph_data.get("edges", [])
papers = graph_data.get("papers", [])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/graph")
def get_graph():
    country = request.args.get("country")
    subfield = request.args.get("subfield")
    min_year = request.args.get("year", type=int)
    author_query = request.args.get("author", "").lower()
    main_field = request.args.get("main_field")

    filtered_nodes = nodes
    filtered_edges = edges

    if main_field and main_field != "all":
        filtered_nodes = [n for n in filtered_nodes if n.get("main_field") == main_field]
        allowed_ids = {n["id"] for n in filtered_nodes}
        filtered_edges = [e for e in filtered_edges if e["source"] in allowed_ids and e["target"] in allowed_ids]

    if country and country != "all":
        filtered_nodes = [n for n in filtered_nodes if n.get("country") == country]
        allowed_ids = {n["id"] for n in filtered_nodes}
        filtered_edges = [e for e in filtered_edges if e["source"] in allowed_ids and e["target"] in allowed_ids]

    if subfield and subfield != "all":
        filtered_nodes = [n for n in filtered_nodes if n.get("subfield") == subfield]
        allowed_ids = {n["id"] for n in filtered_nodes}
        filtered_edges = [e for e in filtered_edges if e["source"] in allowed_ids and e["target"] in allowed_ids]

    if min_year:
        filtered_edges = [e for e in filtered_edges if e.get("year", 0) >= min_year]
        allowed_ids = {e["source"] for e in filtered_edges} | {e["target"] for e in filtered_edges}
        filtered_nodes = [n for n in filtered_nodes if n["id"] in allowed_ids]

    if author_query:
        filtered_nodes = [n for n in filtered_nodes if author_query in n["id"].lower()]
        allowed_ids = {n["id"] for n in filtered_nodes}
        filtered_edges = [e for e in filtered_edges if e["source"] in allowed_ids or e["target"] in allowed_ids]

    return jsonify({"nodes": filtered_nodes, "edges": filtered_edges})

@app.route("/api/filters")
def get_filters():
    countries = sorted({n.get("country", "Unknown") for n in nodes})
    subfields = sorted({n.get("subfield", "Unknown") for n in nodes})
    years = sorted({e.get("year", 0) for e in edges if "year" in e})

    return jsonify({
        "countries": countries,
        "subfields": subfields,
        "years": {"min": min(years) if years else None, "max": max(years) if years else None}
    })

@app.route("/api/main_fields")
def get_main_fields():
    return jsonify(sorted({n.get("main_field","Unknown") for n in nodes}))

@app.route("/api/paper/<paper_id>")
def get_paper(paper_id):
    for p in papers:
        if p["paper_id"] == paper_id:
            return jsonify(p)
    return jsonify({"error":"Paper not found"}),404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
