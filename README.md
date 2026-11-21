# NOFACE — Anonymous Global Chat

NOFACE is a web-based anonymous chat application that lets people communicate in a shared global chat without displaying their real names.

## Live Demo

https://noface.streamlit.app/

## Features

- **Anonymous chatting:** Users are represented by automatically generated anonymous IDs.
- **Real-time messaging:** New messages appear live using Supabase Realtime.
- **Online user count:** Shows the number of currently active users.
- **Session-based chat visibility:** A user's chat view starts from their session join time, so earlier messages are not shown to newly started sessions.
- **Automatic message cleanup:** Messages older than 24 hours are scheduled for deletion from the database.

> **Privacy note:** NOFACE is anonymous to other chat participants, but it is not a private or end-to-end encrypted messaging service. Messages are stored in the project's Supabase database and may be accessible to the project administrator while they remain stored. Do not share passwords, personal details, or other sensitive information in the chat.

## Tech Stack

- Python
- Streamlit
- Supabase
- PostgreSQL
- Supabase Realtime
- GitHub
- Streamlit Community Cloud

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/shlokgupta0920/NOFACE.git
cd NOFACE
```

### 2. Install dependencies

It is recommended to use a virtual environment.

```bash
python -m venv .venv
```

Activate it:

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

Install the project requirements:

```bash
pip install -r requirements.txt
```

### 3. Configure Supabase credentials

Create a `.env` file in the project root and add your Supabase project URL and **publishable/anon key**:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_publishable_or_anon_key
```

Never commit `.env` or expose a Supabase `service_role` key. Keep secrets in Streamlit Community Cloud's app Secrets settings when deploying.

### 4. Start the app

```bash
streamlit run app.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`).

## Deployment

NOFACE is deployed using Streamlit Community Cloud. To deploy your own copy:

1. Fork or clone this repository.
2. Create/configure your Supabase project and required database tables and Realtime settings.
3. Add the required Supabase credentials in Streamlit Community Cloud → App → Settings → Secrets.
4. Deploy the repository with `app.py` as the main file.

## Contributing

Suggestions, bug reports, and improvements are welcome. Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
