# Student Commute Survey

A Streamlit research app exploring how students travel to campus, how long their commutes take, and which factors influence transport choices.

## Project overview

The application collects voluntary survey responses and presents aggregated insights about:
- the most common transport options;
- one-way commute duration;
- daily transport spending;
- satisfaction with the commute;
- factors that influence transport choice.

The dashboard displays grouped statistics only after at least five responses have been collected. Individual survey records are not exposed through the public dashboard.

## Tech stack

- Python
- Streamlit
- Supabase (PostgreSQL)
- Plotly
- pandas
- GitHub Actions

## Run locally

1. Install Python 3.10 or newer.
2. Clone this repository:
   ```bash
   git clone https://github.com/gafinmarsel-ops/-.git student-commute-survey
   cd student-commute-survey
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure Streamlit secrets in `.streamlit/secrets.toml`:
   ```toml
   SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
   SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```

Never put a Supabase service-role key in the app or commit secrets to Git.

## Supabase setup

1. Open the SQL Editor in your Supabase project.
2. Review `supabase/setup.sql` and confirm it matches your existing database before running it.
3. Run the script.
4. Add `SUPABASE_URL` and the public anon/publishable key to Streamlit Community Cloud secrets.

The app inserts survey answers into `survey_responses` and reads dashboard data only through the `get_survey_stats()` database function. Row-level security is enabled; public users are not granted direct access to individual response rows.

If you already have a `survey_responses` table from an earlier version, inspect its columns and policies before applying the setup script. `CREATE TABLE IF NOT EXISTS` does not migrate an existing table.

## Deployment

Deploy the repository with [Streamlit Community Cloud](https://share.streamlit.io/), select `app.py` as the entry point, and add the two Supabase secrets in the app settings.

## Repository structure

```text
.
├── .github/workflows/quality.yml
├── .gitignore
├── app.py
├── requirements.txt
├── README.md
└── supabase/
    └── setup.sql
```

## Privacy notes

- The survey does not ask for names, email addresses, or phone numbers.
- The optional free-text field should not contain identifying information.
- Public dashboard output is aggregated and small groups are suppressed.
- This is an educational project, not a certified anonymity or privacy service. Review your database provider's logging and retention settings before collecting real-world data.

## Author

Marcel Gafin

## License

MIT
