FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY microgrid/ microgrid/

USER 10001
CMD ["python", "-c", "from microgrid.byzantine_consensus import WMSRConsensusCoordinator; print('Microgrid Consensus Engine Online.')"]