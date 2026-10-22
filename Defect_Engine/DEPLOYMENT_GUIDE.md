# DefectMind Online Cloud Deployment Guide
## Deploying Backend to Render, Frontend to Vercel, and Database to Supabase

This guide walks you through deploying **DefectMind** to production across cloud providers:
- **Database**: [Supabase](https://supabase.com/) (Managed PostgreSQL for persisting defect diagnoses and resolutions)
- **Backend API & Multi-Agent Pipeline**: [Render](https://render.com/) (FastAPI + LangGraph + ChromaDB)
- **Frontend Developer Dashboard**: [Vercel](https://vercel.com/) (Next.js 14 Glassmorphism Web App)

---

## Architecture Overview

```
 [User Browser] 
       │
       ▼
 [Vercel: Next.js Frontend]
  (NEXT_PUBLIC_API_URL=https://defectmind-backend.onrender.com/api/v1)
       │
       ▼ REST HTTP & Multipart Form Data
 [Render: FastAPI Backend & Multi-Agent Pipeline]
  ├── LangGraph State Machine (5 Autonomous Diagnostic Agents)
  ├── ChromaDB Vector Store (Auto-seeded RAG Knowledge Base)
  └── Supabase PostgreSQL Connection (asyncpg)
       │
       ▼ SSL Encrypted Connection
 [Supabase: PostgreSQL Database]
  └── Table: bug_submissions (Persistent defect diagnoses, agent JSON logs, resolution state)
```

---

## Part 1: Set Up Supabase Database (PostgreSQL)

Supabase provides a free, persistent PostgreSQL database with automatic backups and an interactive SQL editor.

### Step 1.1: Create a Supabase Project
1. Log in to [Supabase](https://supabase.com/).
2. Click **New Project** and name it `defectmind-db`.
3. Choose a strong database password and select your closest AWS region.
4. Wait ~1 minute for Supabase to provision the database.

### Step 1.2: Obtain the Database Connection URI
1. In your Supabase project dashboard, navigate to **Project Settings** (gear icon at the bottom left) &rarr; **Database**.
2. Scroll to the **Connection string** section.
3. Select the **URI** tab:
   - **Direct Connection** (Port 5432):
     ```text
     postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
     ```
   - **Connection Pooler / Supavisor** (Port 6543 or 5432):
     ```text
     postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
     ```
4. Replace `[YOUR-PASSWORD]` with your actual database password.

> [!NOTE]
> DefectMind automatically translates `postgres://` or `postgresql://` URIs into `postgresql+asyncpg://`, configures SSL encryption, and sets `statement_cache_size=0` for full compatibility with Supabase's transaction poolers. You do **not** need to manually run any SQL table creation scripts; the backend automatically creates and migrates all required tables on startup!

---

## Part 2: Deploy Backend to Render

Render will host the FastAPI REST API, run the 5-agent LangGraph pipeline, and maintain the ChromaDB vector store.

### Step 2.1: Push Your Code to GitHub
Ensure your repository is pushed to GitHub:
```bash
git add .
git commit -m "feat: configure Supabase database, Render backend, and Vercel frontend"
git push origin main
```

### Step 2.2: Create a New Web Service on Render
1. Log in to [Render](https://render.com/).
2. Click **New +** &rarr; **Web Service**.
3. Connect your GitHub repository containing `Defect_Engine`.
4. Configure the Web Service settings:
   - **Name**: `defectmind-backend` (or a name of your choice)
   - **Region**: Choose the same or closest region to your Supabase project
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

### Step 2.3: Set Environment Variables on Render
Scroll to the **Environment Variables** section and add the following keys:

| Key | Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres` | Your Supabase connection URI |
| `BACKEND_CORS_ORIGINS` | `https://*.vercel.app,http://localhost:3000` | Allows your Vercel frontend to make API calls |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | Storage path for ChromaDB dense vectors |
| `RATE_LIMIT_ENABLED` | `True` | Enables DDoS & rate limit protection |
| `SUBMISSION_RATE_LIMIT` | `15/minute` | Rate limit for multi-agent defect submissions |
| `DEFAULT_RATE_LIMIT` | `60/minute` | General API rate limit |
| `OPENAI_API_KEY` | *(Optional)* `sk-...` | Optional OpenAI key for fallback LLM reasoning |

### Step 2.4: Deploy and Verify Backend
1. Click **Create Web Service**.
2. Render will build the service, install dependencies, initialize Supabase tables, and auto-seed ChromaDB baseline historical defects.
3. Once deployed, note down your Render service URL:
   `https://defectmind-backend.onrender.com`
4. Test the health check in your browser:
   `https://defectmind-backend.onrender.com/health` &rarr; Should return `{"status":"healthy"}`.
5. Interactive Swagger documentation will be live at:
   `https://defectmind-backend.onrender.com/docs`

---

## Part 3: Deploy Frontend to Vercel

Vercel provides instant hosting, global CDN edge delivery, and automatic SSL for Next.js 14.

### Step 3.1: Import Project into Vercel
1. Log in to [Vercel](https://vercel.com/).
2. Click **Add New...** &rarr; **Project**.
3. Select your GitHub repository.
4. In the configuration screen:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click **Edit** and select `frontend`

### Step 3.2: Configure Environment Variables on Vercel
In the **Environment Variables** section, add:

| Key | Value |
| :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `https://defectmind-backend.onrender.com/api/v1` *(use your actual Render URL)* |

> [!IMPORTANT]
> Make sure `NEXT_PUBLIC_API_URL` ends with `/api/v1` and matches your Render backend URL.

### Step 3.3: Deploy
1. Click **Deploy**.
2. Vercel will compile the Next.js application, optimize client bundles, and provision your live domain:
   `https://defectmind.vercel.app` (or your chosen project slug).

---

## Part 4: End-to-End Verification Checklist

Once both Render and Vercel deployments are live, test the following workflows:

1. **Bug Submission & Multi-Agent Diagnosis**:
   - Open your Vercel frontend URL.
   - Click any sample preset button (e.g. **Kafka OOM / NullPointer** or **Gecko C++ Segfault**).
   - Click **Run Multi-Agent Triage Pipeline**.
   - Verify that the 5-agent pipeline returns the structured findings report (Triage, Log Analysis, Root Cause, Duplicate Matrix, and Unified Diff Patch).

2. **Persistent Storage in Supabase**:
   - Check the **Defect History** drawer on the left panel.
   - The newly submitted bug should appear with its severity and priority badge.
   - Open your Supabase Dashboard &rarr; **Table Editor** &rarr; `bug_submissions`.
   - Verify that the new defect record is saved with `parsed_log_json`, `root_cause_json`, `duplicate_json`, `remediation_json`, and `similar_bugs_json`.

3. **Knowledge Base Growth Feedback Loop**:
   - In the **Diagnosis Report** tab, scroll to the **Knowledge Base Continuous Growth** card.
   - Click **Confirm Fix & Ingest into Knowledge Base**.
   - Verify that the status turns to **"Resolved & Ingested into Vector Knowledge Base"** and the Defect History badge updates to **Resolved & Ingested**.

4. **Defect Pattern Analytics**:
   - Click the top navigation tab **Pattern Analytics**.
   - Verify the Systemic Defect Health score, component risk index distribution, recurring failure themes, and architectural action plan.
