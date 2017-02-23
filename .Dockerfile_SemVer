FROM centos:7

MAINTAINER RightBrain Networks "ops+docker@rightbrainnetworks.com"

RUN yum update -y && yum install -y epel-release

RUN yum install -y git

RUN yum install -y python-pip
RUN pip install --upgrade pip

RUN useradd -d /semver semver
WORKDIR /semver

ADD ./ /semver
RUN chown -R semver:semver /semver && chmod -R ug+x /semver/*

RUN pip install -r requirements.txt

CMD python get_version.py
