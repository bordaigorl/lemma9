FROM python:2

WORKDIR /usr/src/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "pytest", "-s", "./tests/test_Timing.py" ]
