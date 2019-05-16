FROM python:3
COPY . /code
WORKDIR /code
RUN pip install flask
RUN pip install flask-cors
EXPOSE 5000
CMD ["python","Main.py"]