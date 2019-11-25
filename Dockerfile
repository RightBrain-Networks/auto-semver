FROM centos/python-36-centos7
 
USER root

#Perform updates
RUN pip install --upgrade pip
RUN yum update -y

#Setup semver
ADD / /semver
WORKDIR /semver
RUN python setup.py sdist
RUN pip install dist/semver-*.tar.gz

# Prep workspace
RUN mkdir /workspace
WORKDIR /workspace
VOLUME /workspace

#Permissions
RUN useradd -d /semverUser semverUser
RUN chown -R semverUser:semverUser /workspace

ENTRYPOINT [ "semver" ]

USER semverUser