import os
import time
import yaml
import argparse
from rich.console import Console

from ingest import DataIngestionAgent
from analytics import AnalyticsAgent
from llm_agent import LLMQueryAgent
from upload_agent import UploadAgent

console = Console()

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def ensure_folders(config):
    for f in [config['csv_folder'], config['txt_folder'], config['output_folder']]:
        os.makedirs(f, exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="Agentic Analytics System")
    parser.add_argument("--ingest", type=str, help="Path to a new CSV file to upload/ingest")
    parser.add_argument("--new_txt", type=str, help="Path to a new TXT folder (use with --ingest)")
    args = parser.parse_args()

    config = load_config()
    ensure_folders(config)

    # Initialize Agents
    ingest_agent = DataIngestionAgent(config['csv_folder'], config['txt_folder'])
    analytics_agent = AnalyticsAgent(config['output_folder'])
    upload_agent = UploadAgent(config['csv_folder'], config['txt_folder'])
    llm_agent = LLMQueryAgent(config['ollama_model'], config['ollama_url'], config['max_context_records'])

    # CLI override for uploading new data
    if args.ingest:
        upload_agent.upload_dataset(args.ingest, args.new_txt)

    console.print("[bold cyan]Starting Database Ingestion...[/bold cyan]")
    ingest_agent.load_data()
    ingest_agent.print_summary()
    
    # Start background watcher for hot-reloads
    observer = ingest_agent.start_watcher()

    try:
        while True:
            console.print("\n[bold]Options:[/bold]")
            console.print("1. View Precomputed Analytics")
            console.print("2. Ask LLM Question")
            console.print("3. Exit")
            choice = input("\nEnter choice > ")

            df, txt_data = ingest_agent.get_dataframe()

            if choice == "1":
                analytics_agent.run_all_analytics(df)
            elif choice == "2":
                q = input("\nEnter your question > ")
                llm_agent.process_query(q, df, txt_data)
            elif choice == "3":
                console.print("[blue]Exiting...[/blue]")
                break
            else:
                console.print("[red]Invalid choice.[/red]")
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main()