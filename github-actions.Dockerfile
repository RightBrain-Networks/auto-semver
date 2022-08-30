FROM centos/python-36-centos7
 
USER root

#Perform updates
RUN pip install --upgrade pip
RUN yum update -y
RUN yum -y remove git
RUN yum -y install https://packages.endpoint.com/rhel/7/os/x86_64/endpoint-repo-1.7-1.x86_64.rpm
RUN yum -y install git

#Setup semver
ADD / /semver
WORKDIR /semver
RUN python setup.py sdist
RUN pip install dist/semver-*.tar.gz

CMD [ "semver" ]
