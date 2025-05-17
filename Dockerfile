# Use Kali Linux Rolling as Base Image
FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive

# Install required dependencies
RUN apt-get update && apt-get install -y \
    curl dnsutils wget vim git build-essential \
    libssl-dev libffi-dev zlib1g-dev \
    libsqlite3-dev libncurses5-dev libgdbm-dev \
    libnss3-dev libreadline-dev libbz2-dev liblzma-dev \
    python3-venv python3-pip

# Install Python 3.10.12 manually
WORKDIR /usr/src
RUN wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz && \
    tar -xvf Python-3.10.12.tgz && \
    cd Python-3.10.12 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && make altinstall && \
    rm -rf /usr/src/Python-3.10.12*

# Set Python 3.10.12 as default
RUN ln -sf /usr/local/bin/python3.10 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3.10 /usr/bin/pip3

# Verify installation
RUN python3 --version && pip3 --version

# Install additional dependencies
RUN apt-get install -y nmap sqlmap autopsy john
RUN apt-get install -y zaproxy docker.io
RUN pip3 install zaproxy --break-system-packages

# Install Google Chrome
WORKDIR /home/
RUN apt-get install -y wget gnupg2 software-properties-common && \
    wget -q -O /usr/share/keyrings/google-chrome-keyring.gpg https://dl-ssl.google.com/linux/linux_signing_key.pub && \
    echo "deb [signed-by=/usr/share/keyrings/google-chrome-keyring.gpg arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | \
    tee /etc/apt/sources.list.d/google-chrome.list > /dev/null && \
    apt-get update && apt-get install -y google-chrome-stable
WORKDIR /root/

# Install RustScan
RUN wget https://github.com/RustScan/RustScan/releases/download/2.2.2/rustscan_2.2.2_amd64.deb && \
    dpkg -i rustscan_2.2.2_amd64.deb && \
    rm rustscan_2.2.2_amd64.deb
RUN apt-get install -y iputils-ping

# Clean up unnecessary files
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Nettacker manually
RUN mkdir /opt/nettacker && \
    git clone https://github.com/OWASP/Nettacker.git /opt/nettacker && \
    apt-get remove -y python3-cryptography
RUN chmod +x /opt/nettacker/nettacker.py && \
    ln -s /opt/nettacker/nettacker.py /usr/local/bin/nettacker

# Create and activate virtual environment
WORKDIR /root/
RUN python3 -m venv /root/venv
ENV PATH="/root/venv/bin:$PATH"

# Install project's dependencies inside venv
COPY . /root/
RUN /root/venv/bin/pip install --no-cache-dir --use-deprecated=legacy-resolver -r /root/requirements.txt 

WORKDIR /root/mayaegis/

# Expose port and set entry point
EXPOSE 8501
ENTRYPOINT ["/bin/bash", "-c", "source /root/.env && source /root/venv/bin/activate && exec streamlit run /root/frontend/main.py --server.port=8501 --server.address=0.0.0.0"]