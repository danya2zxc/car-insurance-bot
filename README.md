# Car Insurance Bot

![CI/CD](https://github.com/danya2zxc/car-insurance-bot/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A sophisticated Telegram bot that automates car insurance sales. It leverages OCR to process documents, AI to generate policies and handle conversations, and a robust FSM to guide users through the entire workflow.

---

## 🚀 Live Demo

The bot is deployed and live on Railway. You can interact with it here:

**[>> Click to start a chat with the bot <<](https://t.me/Auto_Insure_bot)** 


---

## ✨ Features

-   **🤖 AI-Powered Conversations:** Uses OpenAI (`gpt-4o-mini`) to handle unexpected user messages and generate final policy documents in HTML format.
-   **📄 Automated Document Processing:** Integrates with the Mindee API to extract data from user-submitted photos of passports and vehicle documents.
-   **⚙️ Robust State Management:** A full Finite State Machine (FSM) built with `aiogram` guides the user through the process, with persistent state stored in **Redis**.
-   **✅ Interactive Confirmation Flow:** Users can review extracted data at each step, confirm its accuracy, or choose to re-upload specific documents.
-   **🐳 Containerized & Deployable:** Fully containerized with **Docker** and includes a `docker-compose.yml` for easy local setup.
-   **🧪 Comprehensive Testing:** Includes a suite of unit and integration tests using `pytest` to ensure code quality and reliability.
-   **👷 Continuous Integration:** A full CI/CD pipeline using **GitHub Actions** automatically runs linters (`Ruff`) and tests on every push.
-   **🛠️ Developer-Friendly:** Comes with a `Makefile` for streamlined local development commands (`run`, `test`, `lint`, etc.).

---

## 🛠️ Tech Stack

-   **Bot Framework:** `aiogram 3`
-   **AI & NLP:** `OpenAI API`
-   **OCR / Document AI:** `Mindee API`
-   **Database / Caching:** `Redis` (for FSM storage)
-   **Containerization:** `Docker` & `Docker Compose`
-   **CI/CD:** `GitHub Actions`
-   **Testing:** `pytest`, `pytest-asyncio`
-   **Code Quality:** `Ruff`
-   **Dependency Management:** `Poetry`

---

## 🏁 Quick Start

You can run this project locally using either Docker (recommended) or Poetry directly.

### Option 1: Running with Docker (Recommended)

This is the easiest way to get started, as it handles Redis and all dependencies automatically.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/danya2zxc/car-insurance-bot.git
    cd car-insurance-bot
    ```

2.  **Create and configure your environment file:**
    ```bash
    cp .env.example .env
    ```
    Now, open the `.env` file and fill in your API keys and tokens.

3.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    The bot and Redis will start up. To stop, press `Ctrl+C`.

### Option 2: Running with Poetry

Use this method if you prefer to manage the Python environment manually.

1.  **Prerequisites:**
    *   Python 3.11+
    *   Poetry installed
    *   A running Redis instance

2.  **Clone and install dependencies:**
    ```bash
    git clone https://github.com/danya2zxc/car-insurance-bot.git
    cd car-insurance-bot
    poetry install
    ```

3.  **Create and configure your environment file:**
    ```bash
    cp .env.example .env
    ```
    Open `.env` and fill in your API keys, tokens, and ensure `REDIS_URL` points to your Redis instance (e.g., `redis://localhost:6379/0`).

4.  **Run the bot:**
    The project includes a `Makefile` for convenience.
    *   For a single run:
        ```bash
        make run
        ```
    *   For development with auto-reloading on file changes:
        ```bash
        make start
        ```

---

## 📂 Project Structure

```
.
├── app/                # Main application source code
│   ├── services/       # External API clients (Mindee, OpenAI)
│   ├── utils/          # Helper functions
│   ├── config.py       # Pydantic settings management
│   ├── handlers.py     # Aiogram message and callback handlers
│   ├── keyboard.py     # Inline keyboard layouts
│   ├── main.py         # Bot entry point
│   ├── models.py       # Pydantic data models
│   ├── processors.py   # Business logic for processing data
│   └── states.py       # FSM states
├── tests/              # Unit and integration tests
│   ├── integration/
│   └── unit/
├── .github/workflows/  # CI/CD pipeline configuration
├── .env.example        # Environment variable template
├── Dockerfile          # Production Docker image definition
├── docker-compose.yml  # Local development setup
├── Makefile            # Development command shortcuts
└── pyproject.toml      # Project dependencies and configuration
└── LICENSE             # Project license file
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

