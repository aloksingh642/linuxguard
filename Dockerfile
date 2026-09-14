FROM python:3.12-slim

WORKDIR /app

ARG LINUXGUARD_UID=1000
ARG LINUXGUARD_GID=1000

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd --gid ${LINUXGUARD_GID} linuxguard && \
    useradd \
    --uid ${LINUXGUARD_UID} \
    --gid ${LINUXGUARD_GID} \
    --create-home \
    linuxguard

RUN chown -R ${LINUXGUARD_UID}:${LINUXGUARD_GID} /app

USER linuxguard

EXPOSE 8000
EXPOSE 8501

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
