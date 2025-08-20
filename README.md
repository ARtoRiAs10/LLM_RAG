# LLM Specialist Assignment: A Cloud-Native RAG Pipeline

This project implements a complete, containerized Retrieval-Augmented Generation (RAG) pipeline. It allows users to upload PDF documents and ask questions based on their content. The architecture is designed to be modern, scalable, and resource-friendly by leveraging managed cloud services for databases and self-hosting only the necessary compute components.

## Final Technology Stack

- **Backend API:** FastAPI
- **Metadata Database:** [NeonDB](https://neon.tech/) (Cloud-hosted, Serverless PostgreSQL)
- **Vector Database:** [Qdrant Cloud](https://cloud.qdrant.io/) (Cloud-hosted, Managed Vector DB)
- **LLM Service:** [Ollama](https://ollama.ai/) (Self-hosted via Docker, serving the `phi` model)
- **Embeddings Model:** Hugging Face `all-MiniLM-L6-v2`
- **Orchestration:** LangChain
- **Containerization:** Docker & Docker Compose
- **Project Structure:** Standard `src/app` layout for robust Python imports.

## Prerequisites

- Git
- Docker and Docker Compose
- A free [NeonDB](https://neon.tech/) account
- A free [Qdrant Cloud](https://cloud.qdrant.io/) account

## Setup and Installation

### 1. Get Cloud Credentials

1.  **NeonDB (PostgreSQL):**
    - Sign up at [neon.tech](https://neon.tech) and create a new project.
    - From your project dashboard, copy the full **PostgreSQL connection string**.
    - **Important:** If your string contains `?sslmode=require` at the end, change it to `?sslmode=require` for better compatibility in this environment.

2.  **Qdrant Cloud (Vector DB):**
    - Sign up at [cloud.qdrant.io](https://cloud.qdrant.io) and create a free 1GB cluster.
    - Once the cluster is active, copy its **Cluster URL** and create/copy a new **API Key**.

### 2. Configure the Project

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd <repo-name>
    ```

2.  **Create `.env` File:**
    - Create a file named `.env` in the project's root directory.
    - Copy the content below and paste in your actual credentials.

    ```ini
    # --- CORE SETTINGS ---
    PROJECT_NAME="Open Source RAG API"

    # --- NEON DATABASE ---
    DATABASE_URL="YOUR_NEON_DB_CONNECTION_STRING_HERE"

    # --- QDRANT CLOUD ---
    QDRANT_URL="YOUR_QDRANT_CLOUD_URL_HERE"
    QDRANT_API_KEY="YOUR_QDRANT_CLOUD_API_KEY_HERE"

    # --- OLLAMA LLM SERVICE ---
    OLLAMA_BASE_URL="http://ollama:11434"
    ```

### 3. Build and Run the Services

1.  **Start Docker Containers:**
    - From the project root, run:
    ```bash
    docker-compose up --build -d
    ```
    - This will build and start the `api` and `ollama` services.

2.  **Download the LLM (One-Time Step):**
    - The Ollama container needs to download the model. We use `phi` as it's small and works well in resource-constrained environments.
    ```bash
    docker-compose exec ollama ollama pull phi
    ```
    - The system is now fully running!

## API Usage with Postman

### 1. Expose the API Port

- In environments like GitHub Codespaces, go to the **PORTS** tab.
- Find the line for **Port 8001**.
- Set its visibility to **Public**.
- Copy the public URL provided. This is your **Base URL**.

### 2. Configure Postman

1.  Create a new collection.
2.  Go to the "Variables" tab and create a variable named `baseUrl`.
3.  Paste the public URL for port 8001 as its value.
4.  Create the following requests:

---

### **Endpoint Testing Commands**

#### **A. Upload Document**
- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/documents`
- **Body:**
  - Select `form-data`.
  - Add a key `file`, change its type to `File`, and select a PDF from your machine.
- **Headers:** Do not set a `Content-Type` header manually. Let Postman handle it.
- **Expected Success:** `201 Created` with document metadata.

#### **B. Get Document Status**
- **Method:** `GET`
- **URL:** `{{baseUrl}}/api/v1/documents/1` (replace `1` with an ID from the upload response)
- **Expected Success:** `200 OK` with document metadata.

#### **C. Query the System**
- **Method:** `POST`
- **URL:** `{{baseUrl}}/api/v1/query`
- **Body:**
  - Select `raw` and `JSON`.
  - Provide a valid JSON body:
    ```json
    {
        "query": "What is the main objective of this document?"
    }
    ```
- **Headers:** Ensure no manual `Content-Type` is set.
- **Expected Success:** `200 OK` with the RAG response.

## Troubleshooting

- **`502 Bad Gateway` or "Site can't be reached":** Your `api` container has crashed. Run `docker-compose logs api` to find the Python traceback. The most common cause is an incorrect URL or API key in your `.env` file.
- **`401 Unauthorized`:** Your API port is set to "Private" in Codespaces. Change it to "Public".
- **`422 Unprocessable Entity` on Upload:** Your Postman request is missing the file. Check the `Body -> form-data` tab.
- **`400 Bad Request` on Query:** The body of your query request is not valid JSON. Check for typos, use double quotes, and ensure the `Body -> raw -> JSON` setting is correct in Postman.
- **Ollama Error `process has terminated`:** You are out of memory. Switch to a smaller model like `phi` or `tinyllama`.