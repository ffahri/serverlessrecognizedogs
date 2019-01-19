FROM gcr.io/dynamic-now-218617/python3base
RUN pip3 install twilio
RUN mkdir app
ADD app.py /app
WORKDIR /app
EXPOSE 8080
CMD ["python3","app.py"]
