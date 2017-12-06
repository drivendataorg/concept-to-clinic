FROM concepttoclinic_base

# Copy the scripts into the container
COPY ./compose/interface/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./compose/interface/start-dev.sh /start-dev.sh
RUN sed -i 's/\r//' /start-dev.sh
RUN chmod +x /start-dev.sh

# Add expose to API so it can be developed on its own
EXPOSE 8000

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
