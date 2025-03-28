FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip wget tar gzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies first for better caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Create and set up TreeTagger
RUN mkdir /app/treetagger && \
    cd /app/treetagger && \
    wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tree-tagger-linux-3.2.4.tar.gz && \
    tar -xzf tree-tagger-linux-3.2.4.tar.gz && \
    wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tagger-scripts.tar.gz && \
    tar -xzf tagger-scripts.tar.gz && \
    wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/english.par.gz && \
    gunzip english.par.gz && \
    mv english.par /app/treetagger/lib/ && \
    wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/install-tagger.sh && \
    chmod +x install-tagger.sh && \
    ./install-tagger.sh 

#RUN groupadd docker \
#    && useradd -g docker docker

#RUN chown -R docker:docker /app/

#USER docker

# Verifica si existe
#RUN if [ -e "/app/treetagger/bin/tree-tagger" ]; then \
#        chmod +x /app/treetagger/bin/tree-tagger; \
#    fi && \
#    if [ -d "/app/treetagger" ]; then \
#        chmod +x /app/treetagger/; \
#    fi

# Establecer el directorio de trabajo para que las rutas sean relativas
WORKDIR /app

# Establecer permisos adecuados para TreeTagger
RUN find /app/treetagger/ -type f -exec chmod 775 {} \;

# Expose the Flask application's port
EXPOSE 5000

# Run the Flask application
CMD ["python3", "app.py"]





