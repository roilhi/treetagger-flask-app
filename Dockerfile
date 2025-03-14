FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip wget tar gzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory for the app
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Create and set up TreeTagger outside the app directory
RUN mkdir /treetagger && \
    cd /treetagger && \
    wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tree-tagger-linux-3.2.4.tar.gz && \
    tar -xzf tree-tagger-linux-3.2.4.tar.gz && \
    wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tagger-scripts.tar.gz && \
    tar -xzf tagger-scripts.tar.gz && \
    wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/install-tagger.sh && \
    chmod +x install-tagger.sh && \
    ./install-tagger.sh && \
    wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/english.par.gz

# Expose the Flask application's port
EXPOSE 5000

# Run the Flask application
CMD ["python3", "app.py"]



