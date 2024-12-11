FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y libzbar0
RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "Anasayfa.py", "--server.port=8501", "--server.enableCORS=false"]