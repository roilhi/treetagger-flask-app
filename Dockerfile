FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app

# Copy and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for TreeTagger
RUN mkdir /app/treetagger && cd /app/treetagger 

# Download and extract TreeTagger binaries and scripts
RUN apt-get update && apt-get install -y wget tar gzip && \
    wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tree-tagger-linux-3.2.4.tar.gz && \
    tar -xzf tree-tagger-linux-3.2.4.tar.gz && \
    wget https://cis.lmu.de/~schmid/tools/TreeTagger/data/tagger-scripts.tar.gz && \
    gunzip tagger-scripts.tar.gz && \
    wget https://cis.lmu.de/~schmid/tools/TreeTagger/data/install-tagger.sh && \
    wget https://cis.lmu.de/~schmid/tools/TreeTagger/data/english.par.gz 

# Ensure that install-tagger.sh exists and is executable
RUN sh install-tagger.sh 

# Expose the Flask application's port
EXPOSE 5000

# Run the Flask application
CMD ["python3", "app.py"]



