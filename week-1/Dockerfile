FROM python:3.10-alpine3.16
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements.txt
RUN addgroup user && adduser -u 9999 -G user -D user
USER user
ENV PATH="${PATH}:/home/user/.local/bin/"
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python3", "app.py"]
