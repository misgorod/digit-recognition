FROM python:3.5

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#COPY ./src ./src

WORKDIR /app/src

VOLUME [ "/app/src" ]

EXPOSE 8000
EXPOSE 8001

CMD [ "adev", "runserver", "/app/src/app.py", "--verbose", "--root", "/app", "--static", "/app/src/static", "--livereload", "--debug-toolbar", "--host", "0.0.0.0"]