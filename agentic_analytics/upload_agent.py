import os
import shutil
import pandas as pd
from rich.console import Console

console = Console()

class UploadAgent:
    """Agent responsible for uploading and appending new data seamlessly."""
    def __init__(self, csv_folder, txt_folder):
        self.csv_folder = csv_folder
        self.txt_folder = txt_folder
        
    def upload_dataset(self, csv_path: str, new_txt_folder: str = None):
        """Validates new CSV and copies it into the managed csv_folder."""
        if not os.path.exists(csv_path):
            console.print(f"[red]File {csv_path} does not exist.[/red]")
            return False
            
        # Expected schema check
        expected_columns = ["Unique ID", "Original Date", "Source Platform", 
                            "Fraud Category", "Fraud Subcategory", "Narrative Type", "Notes"]
                            
        try:
            df_new = pd.read_csv(csv_path)
            missing = [c for c in expected_columns if c not in df_new.columns]
            if missing:
                console.print(f"[yellow]Warning: Uploaded CSV is missing expected columns: {missing}[/yellow]")
                
            # Copy to csv folder
            dest = os.path.join(self.csv_folder, os.path.basename(csv_path))
            shutil.copy(csv_path, dest)
            console.print(f"[green]Successfully uploaded CSV to {dest}[/green]")
            
            # Transfer txt files if provided
            if new_txt_folder and os.path.isdir(new_txt_folder):
                for f in os.listdir(new_txt_folder):
                    if f.endswith('.txt'):
                        shutil.copy(os.path.join(new_txt_folder, f), os.path.join(self.txt_folder, f))
                console.print(f"[green]Successfully copied TXT files.[/green]")
                
            return True
        except Exception as e:
            console.print(f"[red]Failed during upload: {e}[/red]")
            return False