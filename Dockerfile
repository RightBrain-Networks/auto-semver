FROM centos/python-36-centos7

MAINTAINER RightBrain Networks "ops+docker@rightbrainnetworks.com"

USER root

#Perform updates
RUN pip install --upgrade pip
RUN yum update -y

#Install reqs
RUN yum install -y epel-release
RUN yum install -y git

#Setup semver
ADD / /semver
WORKDIR /semver
RUN pip install -e .

# Prep workspace
RUN mkdir /workspace
WORKDIR /workspace
VOLUME /workspace

#Permissions
RUN useradd -d /semverUser semverUser
RUN chown -R semverUser:semverUser /workspace

CMD /opt/app-root/bin/semver

USER semverUser