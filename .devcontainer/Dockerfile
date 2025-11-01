FROM mcr.microsoft.com/devcontainers/python:3.11

# Install R
RUN apt-get update && apt-get install -y \
    r-base \
    r-base-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install pandas numpy matplotlib seaborn jupyter \
    psycopg2-binary sqlalchemy ipython-sql \
    polars requests

# Install R packages
RUN R -e "install.packages(c('tidyverse', 'reticulate', 'RPostgreSQL', 'DBI', 'dbplyr', 'nflverse', 'ggthemes'), repos='https://cran.rstudio.com/')"

# Install PostgreSQL client tools
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*