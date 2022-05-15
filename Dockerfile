FROM ubuntu:22.04


RUN apt-get update \
&&  apt-get install -y ffmpeg wget git \
&&  rm -rf /var/lib/apt/lists/*

RUN useradd app \
&&  mkdir /home/app \
&&  chown -R app:app /home/app

USER app

RUN cd /home/app \
&&  wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh \
&&  bash Miniforge3-Linux-aarch64.sh -b -p /home/app/conda \
&&  rm -f Miniforge3-Linux-aarch64.sh

COPY app/ /home/app/app/

RUN cd /home/app/app \
&&  /home/app/conda/bin/pip install --no-cache -r requirements.txt

ENV LISTEN_HOST=0.0.0.0
ENV LISTEN_PORT=2020
ENV TRANSCODE_DIR=/dev/shm/sonos_intercomm
ENV EXTERNAL_HOST=localhost

CMD ["/home/app/app/start.sh"]
