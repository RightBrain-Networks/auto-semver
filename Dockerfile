# ======= #
# Builder #
# ======= #
FROM python:3.11-slim as builder
COPY / /semver
RUN pip wheel --no-cache-dir --wheel-dir /wheels /semver

# ======== #
# Finalize #
# ======== #
FROM python:3.11-slim

# Update and install git
RUN apt-get update && apt-get install -y git

# Create user
RUN mkdir /semver && \
    groupadd -g 10001 semver && \
    useradd -u 10000 -g semver -d /semver semver \
    && chown -R semver:semver /semver

# Prep workspace
RUN mkdir /workspace && \
    chown -R semver:semver /workspace
VOLUME /workspace

# Setup semver
COPY --from=builder /wheels /semver/wheels
RUN pip install --no-cache /semver/wheels/*

USER semver:semver
WORKDIR /workspace
ENTRYPOINT [ "semver" ]
