FROM python:3.9.18-slim-bullseye

RUN apt update && apt upgrade && apt install curl unzip -y && apt install -y procps
# RUN apt-get install -y python3
# RUN apt-get install -y python3-pip
RUN python3 -m pip install paho-mqtt

RUN apt-get install dos2unix
RUN apt-get -y install netcat


COPY nhsups_3.1.36_x86_64_eGLIBC_2.11.zip /tmp/nhscontrol.zip
RUN unzip /tmp/nhscontrol.zip -d /tmp/nhscontrol

RUN cd /tmp/nhscontrol/nhsups_3.1.36_x86_64_eGLIBC_2.11 && chmod +x install.sh && ./install.sh

RUN cd /usr/local/nhs && chmod +x nhsupsserver && chmod +x nhsupsserver.sh
EXPOSE 2001
EXPOSE 2000

WORKDIR /usr/local/nhs/
COPY nhstelnet.py nhstelnet.py
COPY start.sh start.sh

RUN dos2unix start.sh

# ENTRYPOINT ["./nhsupsserver"]
# ENTRYPOINT ["python3", "nhstelnet.py"]
# RUN echo 'iniciando nhscontrol'
# RUN ./nhsupsserver.sh start

# RUN echo 'iniciando app'
# CMD python3 nhstelnet.py
#RUN ./nhsupsserver.sh start


CMD bash start.sh

# ENTRYPOINT ["./nhsupsserver"]