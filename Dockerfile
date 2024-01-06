FROM debian:bullseye

RUN apt update && apt upgrade && apt install curl unzip -y
RUN apt-get install -y python3
#RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

#RUN curl -o /tmp/nhscontrol.zip https://nhs.com.br/wp-content/uploads/2023/11/nhsups_3.1.36_x86_64_eGLIBC_2.11.zip


COPY nhsups_3.1.36_x86_64_eGLIBC_2.11.zip /tmp/nhscontrol.zip
RUN unzip /tmp/nhscontrol.zip -d /tmp/nhscontrol

RUN cd /tmp/nhscontrol/nhsups_3.1.36_x86_64_eGLIBC_2.11 && chmod +x install.sh && ./install.sh

RUN cd /usr/local/nhs && chmod +x nhsupsserver && chmod +x nhsupsserver.sh
EXPOSE 2001
EXPOSE 2000

WORKDIR /usr/local/nhs/
COPY nhstelnet.py nhstelnet.py
COPY start.sh start.sh

#ENTRYPOINT ["./nhsupsserver"]

# RUN echo 'iniciando nhscontrol'
# CMD nhsupsserver.sh start

# RUN echo 'iniciando app'
# CMD python3 nhstelnet.py
#RUN /nhsupsserver.sh start


CMD bash start.sh