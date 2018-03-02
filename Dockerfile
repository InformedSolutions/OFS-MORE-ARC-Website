FROM python:3.5-slim
ENV PYTHONUNBUFFERED 1
ARG PROJECT_SETTINGS

# If dev env install additional packages
RUN  if [ "`echo $PROJECT_SETTINGS | rev | cut -c -3 | rev`" = "dev" ]; then \
       apt-get update; \
       apt-get install -y build-essential graphviz; \
     fi

RUN mkdir /source
RUN mkdir /source/logs
WORKDIR /source
ADD . /source/
RUN pip install -r requirements.txt
RUN chmod +x /source/docker-entrypoint.sh
EXPOSE 8000
CMD ["/source/docker-entrypoint.sh"]
