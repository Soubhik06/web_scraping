import os
import yaml
import json
from flask import Flask, render_template, request, Response, jsonify, Blueprint

from ingest import DataStore
from analytics import AnalyticsAgent
from llm_agent import LLMQueryAgent

# Load config
def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()

# Init globals
data_store = DataStore(config['data_folder'], config['txt_folder'])
data_store.load_data()

analytics_agent = AnalyticsAgent(data_store)
llm_agent = LLMQueryAgent(
    config['ollama_model'], 
    config['ollama_url'], 
    config['max_context_records'], 
    config.get('api_key')
)

# Blueprint setup
bp = Blueprint('main', __name__)

@bp.route("/")
def dashboard():
    stats = analytics_agent.get_dashboard_stats()
    return render_template("index.html", stats=stats)

@bp.route("/analytics")
def analytics_view():
    trends = analytics_agent.get_emerging_trends()
    platforms = analytics_agent.get_platform_contributions()
    heatmap = analytics_agent.get_crosstab_heatmap()
    return render_template("analytics.html", trends=trends, platforms=platforms, heatmap=heatmap)

@bp.route("/explore")
def explore_view():
    df, txt_data = data_store.get_dataframe()
    # Provide top 200 items initially (can be handled via datatables/js client-side)
    records = df.head(200).fillna("").to_dict(orient='records')
    return render_template("explore.html", records=records, txt_data=txt_data)

@bp.route("/query-ui")
def query_ui():
    return render_template("query_ui.html")

@bp.route("/api/chart/<chart_name>")
def chart_data(chart_name):
    if chart_name == "year_wise":
        return jsonify(analytics_agent.get_year_wise_chart())
    elif chart_name == "top_categories":
        return jsonify(analytics_agent.get_top_categories())
    elif chart_name == "narrative_types":
        return jsonify(analytics_agent.get_narrative_distribution())
    return jsonify({"error": "chart not found"}), 404

@bp.route("/query", methods=["POST"])
def query():
    data = request.json
    question = data.get("question", "")
    
    def generate():
        for chunk in llm_agent.process_query_stream(question, data_store):
            yield chunk
            
    return Response(generate(), mimetype='text/plain')

# App factory
app = Flask(__name__)
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)