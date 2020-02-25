FROM python:3.8-slim
RUN  sed -i s@/deb.debian.org@/mirrors.aliyun.com/@g /etc/apt/sources.list \
    && apt-get clean \
    && apt-get update -qq \
    && apt-get install -y build-essential libgmp-dev libpq-dev gcc \
    && pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip install --no-cache-dir uvicorn \
    && mkdir /scheduler-service
WORKDIR /scheduler-service
ADD ./dist/* /scheduler-service/
RUN pip install --no-cache-dir scheduler_*.whl \
    && rm -rf scheduler* \
    && apt-get purge -y --auto-remove gcc build-essential libgmp-dev libpq-dev
EXPOSE 8000
CMD ["uvicorn", "scheduler_service.manage:app", "--host", "0.0.0.0", "--port", "8000"]
