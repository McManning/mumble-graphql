FROM python:3.13-slim

LABEL maintainer="Chase McManning <cmcmanning@gmail.com>"

WORKDIR /app

RUN apt-get update && apt-get install -y python3-zeroc-ice

# Install Ice Python bindings to the site-packages for Python 3.13
RUN ln -s /usr/lib/python3/dist-packages/Ice /usr/local/lib/python3.13/site-packages/Ice && \
    ln -s /usr/lib/python3/dist-packages/IcePy.cpython-313-x86_64-linux-gnu.so /usr/local/lib/python3.13/site-packages/IcePy.cpython-313-x86_64-linux-gnu.so

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY ./src /app

EXPOSE 80
CMD ["fastapi", "run", "app.py", "--port", "80", "--proxy-headers"]
