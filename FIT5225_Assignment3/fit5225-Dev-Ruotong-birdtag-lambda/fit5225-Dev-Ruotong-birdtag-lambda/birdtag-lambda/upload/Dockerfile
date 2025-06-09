FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip libgl1 libglib2.0-0 ffmpeg && \
    apt-get clean

WORKDIR /var/task

COPY requirements.txt .

RUN pip3 install torch==1.13.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV ULTRALYTICS_REQUIREMENTS_AUTO_INSTALL=False
ENV GIT_PYTHON_REFRESH=quiet

ENTRYPOINT ["/usr/bin/python3", "-m", "awslambdaric"]

CMD ["app.lambda_handler"]
