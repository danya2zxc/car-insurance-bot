FROM python:3.11.8-slim


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false 

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*



# Install Poetry and add to PATH in the same RUN
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH for all subsequent RUNs
ENV PATH="/root/.local/bin:$PATH"


# Set working dir
WORKDIR /app

# copy full project
COPY . .


# install project dependencies
RUN poetry install --no-interaction --no-ansi 



#  Run app for development
# CMD ["poetry", "run", "watchmedo", "auto-restart", "--patterns='*.py'", "--recursive","poetry" , "python", "run", "-m", "app.main"]


# Run app
CMD ["poetry", "run", "python", "-m", "app.main"]
