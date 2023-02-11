FROM python:3

# Install docker
RUN cd /usr/bin; \
    curl -L 'https://download.docker.com/linux/static/stable/x86_64/docker-17.06.1-ce.tgz' | tar --strip-components=1 -zxv; \
    pip install docker-compose

# Create webhook dir
RUN mkdir /hook

WORKDIR /hook

# Install requirements
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt && \
    rm -f requirements.txt

# don't run compose in tty
ENV COMPOSE_INTERACTIVE_NO_CLI=1

# Copy in webhook listener script
COPY webhook.py /hook/webhook.py
CMD ["python", "/hook/webhook.py"]
EXPOSE 80
