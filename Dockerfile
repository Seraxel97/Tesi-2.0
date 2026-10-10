FROM python:3.13-slim

LABEL description="Tesi_2.0 — EEG source-space FC pipeline"
LABEL maintainer="Samuele Losio"

# System deps per MNE + scipy + pyvista
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas-dev \
    libgomp1 \
    libgl1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia prima i requirements per cache layer
COPY requirements.txt requirements-dev.txt requirements_docker.txt ./

# INSTALL_EXTRAS: "" (solo pipeline) | "dev" (+pytest, ruff) | "dashboard" (+streamlit, plotly)
ARG INSTALL_EXTRAS=""
RUN pip install --no-cache-dir -r requirements.txt \
    && if [ "$INSTALL_EXTRAS" = "dev" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi \
    && if [ "$INSTALL_EXTRAS" = "dashboard" ]; then pip install --no-cache-dir -r requirements_docker.txt; fi

# Copia codebase (escludi dati pesanti via .dockerignore)
COPY . .

ENV MNE_DATA=/mne_data
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Mount points (da usare con -v)
VOLUME ["/app/data", "/mne_data"]

CMD ["python3", "-c", "print('Tesi_2.0 container ready. Vedi: python3 -m cli.main --help')"]
