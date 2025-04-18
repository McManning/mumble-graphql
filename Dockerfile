FROM python:3.12-alpine

LABEL maintainer="Chase McManning <cmcmanning@gmail.com>"

WORKDIR /app

# deps required for building zeroc-ice
RUN apk add --no-cache \
    libstdc++ \
    make \
    gcc \
    g++ \
    python3-dev \
    py3-setuptools \
    openssl-dev \
    bzip2-dev \
    tiff-dev jpeg-dev openjpeg-dev zlib-dev freetype-dev lcms2-dev \
    libwebp-dev tcl-dev tk-dev harfbuzz-dev fribidi-dev libimagequant-dev \
    libxcb-dev libpng-dev

# Building the wheel for this takes forever. So it sits on its own.
RUN pip install zeroc-ice==3.7.10.1

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY . /app

EXPOSE 80
CMD ["fastapi", "run", "app.py", "--port", "80", "--proxy-headers"]
