FROM python

WORKDIR /main

COPY . /main

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && wget -q https://chromedriver.storage.googleapis.com/89.0.4389.23/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && rm google-chrome-stable_current_amd64.deb chromedriver_linux64.zip

RUN pip install --upgrade pip \
    && pip install Flask==3.0.3 requests==2.25.1 aiobotocore==1.4.2 \
    && pip install selenium==4.20.0 \
    && pip install pandas

CMD ["python", "main.py"]
