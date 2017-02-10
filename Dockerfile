FROM python:2.7-slim
RUN apt-get update -qq && apt-get install -y build-essential libgmp-dev libpq-dev
RUN mkdir /scheduler-service
WORKDIR /scheduler-service
ADD requirements requirements
RUN pip install -r requirements/prod.txt
ADD ./ /scheduler-service/
EXPOSE 8000
CMD ["gunicorn", "manage:app", "--bind", "0.0.0.0:8000"]
