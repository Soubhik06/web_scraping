import pandas as pd

class AnalyticsAgent:
    """Agent exporting data aggregated for the Dashboard and Analytics view JSON APIs."""
    def __init__(self, data_store):
        self.store = data_store

    def get_dashboard_stats(self):
        df, _ = self.store.get_dataframe()
        if df.empty: return {"total_records": 0, "source_breakdown": {}}
        return {
            "total_records": len(df),
            "source_breakdown": df['source_file'].value_counts().to_dict()
        }

    def get_year_wise_chart(self):
        df, _ = self.store.get_dataframe()
        if df.empty or 'Year' not in df.columns: return {"labels": [], "data": []}
        counts = df['Year'].dropna().astype(int).value_counts().sort_index()
        return {"labels": counts.index.tolist(), "data": counts.values.tolist()}

    def get_top_categories(self):
        df, _ = self.store.get_dataframe()
        if df.empty or 'Fraud Category' not in df.columns: return {"labels": [], "data": []}
        counts = df['Fraud Category'].value_counts().head(10)
        return {"labels": counts.index.tolist(), "data": counts.values.tolist()}

    def get_narrative_distribution(self):
        df, _ = self.store.get_dataframe()
        if df.empty or 'Narrative Type' not in df.columns: return {"labels": [], "data": []}
        counts = df['Narrative Type'].value_counts()
        return {"labels": counts.index.tolist(), "data": counts.values.tolist()}

    def get_crosstab_heatmap(self):
        df, _ = self.store.get_dataframe()
        if df.empty or 'Year' not in df.columns or 'Fraud Category' not in df.columns: return {"columns": [], "data": []}
        df_filtered = df.dropna(subset=['Year', 'Fraud Category'])
        ct = pd.crosstab(df_filtered['Fraud Category'], df_filtered['Year'].astype(int))
        
        results = []
        for cat in ct.index:
            row = {"Category": cat}
            for year in ct.columns:
                row[str(year)] = int(ct.loc[cat, year])
            results.append(row)
        return {"columns": ["Category"] + [str(y) for y in sorted(ct.columns)], "data": results}

    def get_emerging_trends(self):
        df, _ = self.store.get_dataframe()
        if df.empty or 'Year' not in df.columns or 'Fraud Category' not in df.columns: return {}
        
        df_2020 = df[df['Year'] > 2020]['Fraud Category'].unique()
        df_pre2020 = df[df['Year'] <= 2020]['Fraud Category'].unique()
        post_2020 = [c for c in df_2020 if pd.notna(c) and c not in df_pre2020]

        df_2022 = df[df['Year'] > 2022]['Fraud Category'].unique()
        df_pre2022 = df[df['Year'] <= 2022]['Fraud Category'].unique()
        post_2022 = [c for c in df_2022 if pd.notna(c) and c not in df_pre2022]

        return {"post_2020": list(post_2020), "post_2022": list(post_2022)}

    def get_platform_contributions(self):
        df, _ = self.store.get_dataframe()
        col = 'Source Platform' if 'Source Platform' in df.columns else 'source_file'
        if df.empty: return []
        counts = df[col].value_counts().reset_index()
        counts.columns = ['Platform', 'Count']
        return counts.to_dict(orient='records')
