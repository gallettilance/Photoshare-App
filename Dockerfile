FROM ubuntu:latest

MAINTAINER Lance Galletti

COPY . /src
WORKDIR /src

RUN apt-get update && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip && \
    apt-get update && \
    pip3 install -r ./requirements.txt
    
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/run/mysqld && \
    chown mysql:mysql /var/run/mysqld && \
    /bin/bash -c "mysqld_safe --skip-grant-tables &" && \
    sleep 5 && \
    mysql -u root -e "create database photoshare" && \
    mysql -u root photoshare < ./database/photoshare.sql 

EXPOSE 5000

ENTRYPOINT ["python3", "./webapp/webapp.py"]
