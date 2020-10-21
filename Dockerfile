FROM neuromcb/afni

RUN apt-get update && \
    apt-get install -y --force-yes \
        lsb-core \
        wget \
        python-pip

RUN wget https://www.nitrc.org/frs/download.php/10144/bxh_xcede_tools-1.11.14-lsb30.x86_64.tgz \
 && tar -xzf bxh_xcede_tools-1.11.14-lsb30.x86_64.tgz \
 && rm bxh_xcede_tools-1.11.14-lsb30.x86_64.tgz

ENV PATH="/bxh_xcede_tools-1.11.14-lsb30.x86_64/bin:${PATH}"

COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
