import requests
import json
from prompts import SYSTEM_PROMPT, LLM_QUERY_TEMPLATE

class LLMQueryAgent:
    """Agent orchestrating retrieval-augmented generation to local Ollama API."""
    def __init__(self, model: str, url: str, max_records: int, api_key: str = None):
        self.model = model
        self.url = url
        self.max_records = max_records
        self.api_key = api_key

    def process_query_stream(self, query: str, data_store):
        """Retrieves contexts, builds prompt, and streams LLM output mapping directly to Flask Response."""
        df, txt_data = data_store.get_dataframe()
        query_lower = query.lower()
        keywords = query_lower.split()
        
        filtered_df = df.copy()
        if 'Fraud Category' in df.columns:
            mask = filtered_df['Fraud Category'].str.lower().apply(lambda x: any(k in str(x) for k in keywords))
            if mask.any():
                filtered_df = filtered_df[mask]
                
        matched_records = filtered_df.head(self.max_records)
        contexts = []
        for _, row in matched_records.iterrows():
            uid = str(row.get('Unique ID', ''))
            cat = str(row.get('Fraud Category', 'Unknown'))
            narr_text = txt_data.get(uid, "No narrative found.")
            contexts.append(f"ID {uid} ({cat}): {narr_text[:300]}...")
            
        context_str = "\n".join(contexts) if contexts else "No relevant narratives found based on initial keyword filter."
        
        stats_str = f"Found {len(filtered_df)} matches conceptually out of {len(df)} total records.\n"
        if 'Fraud Category' in df.columns:
            top_overall = df['Fraud Category'].value_counts().head(10).to_dict()
            stats_str += f"\nTop 10 Cybercrime Categories (by occurrence):\n{json.dumps(top_overall, indent=2)}\n"
            
            if len(filtered_df) != len(df):
                top_filtered = filtered_df['Fraud Category'].value_counts().head(5).to_dict()
                stats_str += f"\nTop 5 Categories in Filtered Results:\n{json.dumps(top_filtered, indent=2)}\n"
        
        final_prompt = LLM_QUERY_TEMPLATE.format(
            question=query,
            stats=stats_str,
            contexts=context_str
        )

        payload = {
            "model": self.model,
            "prompt": final_prompt,
            "system": SYSTEM_PROMPT,
            "stream": True
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = requests.post(self.url, json=payload, headers=headers, stream=True)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    text_chunk = data.get("response", "")
                    yield text_chunk
                    if data.get("done"):
                        break
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                yield f"[Error: Model '{self.model}' not found in Ollama. Please run 'ollama run {self.model}' in your terminal to download it.]"
            else:
                yield f"[Error communicating with Ollama: {str(e)}]"
        except Exception as e:
            yield f"[Error communicating with Ollama: {str(e)}]"
