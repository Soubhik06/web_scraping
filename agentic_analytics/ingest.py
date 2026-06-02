import os
import pandas as pd

class DataStore:
    """Singleton-like datastore for the agentic analytics app."""
    def __init__(self, data_folder, txt_folder):
        self.data_folder = data_folder
        self.txt_folder = txt_folder
        self.df = pd.DataFrame()
        self.txt_data = {}
        self.csv_files = [
            "consumer_complaints.csv", "indiankanoon_complaints.csv",
            "medianama_complaints.csv", "reddit_cities_part1_complaints.csv",
            "reddit_cities_part2_complaints.csv", "reddit_cities_part4_complaints.csv",
            "reddit_cities_part6_complaints.csv", "reddit_cities_part7_complaints.csv",
            "reddit_complaints.csv", "reddit_states_complaints.csv",
            "theprint_complaints.csv"
        ]

    def load_data(self):
        """Loads required CSV files and matching TXT records."""
        print(f"Loading data from {self.data_folder}...")
        df_list = []
        for file_name in self.csv_files:
            path = os.path.join(self.data_folder, file_name)
            if not os.path.exists(path):
                print(f"Warning: {path} not found.")
                continue
            
            try:
                df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip')
            except UnicodeDecodeError:
                df = pd.read_csv(path, encoding='latin-1', on_bad_lines='skip')
            except Exception as e:
                print(f"Error loading {file_name}: {e}")
                continue
            
            df['source_file'] = file_name
            df_list.append(df)

        if df_list:
            self.df = pd.concat(df_list, ignore_index=True)
            # Ensure Year column is consistently parsed
            if 'Original Date' in self.df.columns:
                self.df['Year'] = pd.to_datetime(self.df['Original Date'], errors='coerce').dt.year
            else:
                self.df['Year'] = None
        else:
            self.df = pd.DataFrame()

        # Load corresponding Text Narratives
        print(f"Loading texts from {self.txt_folder}...")
        if os.path.exists(self.txt_folder):
            for file_name in os.listdir(self.txt_folder):
                if file_name.endswith('.txt'):
                    uid = file_name.replace(".txt", "")
                    with open(os.path.join(self.txt_folder, file_name), "r", encoding='utf-8', errors='replace') as f:
                        self.txt_data[uid] = f.read()
        print(f"Loaded {len(self.df)} structured records and {len(self.txt_data)} narratives.")

    def get_dataframe(self):
        return self.df, self.txt_data
