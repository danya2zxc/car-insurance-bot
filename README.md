# Car Insurance Bot

## Description

A Telegram bot that helps users buy car insurance by processing document photos and using AI-powered communication.

> 🚧 **Core workflow implemented.** The bot handles the full document processing and confirmation flow via Mindee API. Next steps: OpenAI integration, testing, and deployment.

## Features

- **FSM-based Workflow:** A clear, stateful conversation flow from start to finish.
- **Passport & Vehicle Document Upload:** Securely handles user photo submissions.
- **Mindee API Integration:** Extracts data from documents in real-time.
- **Interactive Confirmation:** Allows users to confirm data or request changes at each step.
- **Dynamic Keyboards:** User-friendly inline buttons for all interactions.
- **Basic Error Handling:** Gracefully handles invalid photos and API errors.

## Quick Start


## Requirements

- Python 3.11+
- [aiogram](https://docs.aiogram.dev/en/latest/)
- [Mindee API](https://mindee.com/)
- [Poetry](https://python-poetry.org/) for dependency management.
- [OpenAI API](https://platform.openai.com/docs/api-reference/introduction) (for smart chat & document generation)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/danya2zxc/car-insurance-bot
    cd car-insurance-bot
    ```

2.  **Install dependencies:**
    ```bash
    poetry install
    ```

### 3. Environment Variables

1.  Create a `.env` file in the root directory by copying the example:
    ```bash
    cp .env.example .env
    ```

2.  Fill in the required values in the `.env` file.


### 4. Running the Bot

-   **For a single run:**
    ```bash
    make run
    ```
-   **For development with auto-reloading:**
    ```bash
    make start
    ```



---

## Project Status (TODO)

- [x] Telegram bot initialization
- [x] Document upload & Mindee integration
- [x] Data confirmation flows
- [x] Price confirmation
- [x] Basic error handling
- [ ] Dummy policy generation (via OpenAI)
- [ ] Intelligent conversational capabilities (via OpenAI)
- [ ] Add Linters (Ruff, mypy) and Formatters (Black)
- [ ] Add Tests (unit/integration)
- [ ] Deployment to public (e.g., Railway, Render)

---

## License

MIT (or your preferred license)
