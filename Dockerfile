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
RUN pip install wheel
RUN python setup.py sdist bdist_wheel
RUN pip install dist/semver-*.tar.gz

# Prep workspace
RUN mkdir /workspace
WORKDIR /workspace
VOLUME /workspace

#Permissions
RUN useradd -d /semverUser semverUser
RUN chown -R semverUser:semverUser /workspace

CMD [ "semver" ]

USER semverUser
