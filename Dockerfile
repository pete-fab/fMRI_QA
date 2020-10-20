FROM python:2.7.8

RUN wget https://www.nitrc.org/frs/download.php/10144/bxh_xcede_tools-1.11.14-lsb30.x86_64.tgz \
 && tar -xzf bxh_xcede_tools-1.11.14-lsb30.x86_64.tgz \
 && rm bxh_xcede_tools-1.11.14-lsb30.x86_64.tgz

ENV PATH="/bxh_xcede_tools-1.11.14-lsb30.x86_64/bin:${PATH}"

RUN apt-get update 
RUN apt-get install -y --force-yes lsb-core

COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
