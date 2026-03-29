# Build and push:
#   docker buildx build --platform linux/amd64 \
#     -t ghcr.io/max-models/tikzpics/texlive-quarto:latest --push docker/
#
# Run:  docker run --rm ghcr.io/max-models/tikzpics/texlive-quarto:latest

FROM texlive/texlive:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        jq \
        gdebi-core \
    && rm -rf /var/lib/apt/lists/*

RUN QUARTO_VERSION=$(wget -qO- https://api.github.com/repos/quarto-dev/quarto-cli/releases/latest \
        | jq -r '.tag_name' | sed 's/^v//') \
    && ARCH=$(dpkg --print-architecture) \
    && wget -q "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-${ARCH}.deb" \
    && gdebi --non-interactive "quarto-${QUARTO_VERSION}-linux-${ARCH}.deb" \
    && rm "quarto-${QUARTO_VERSION}-linux-${ARCH}.deb"

LABEL org.opencontainers.image.source https://github.com/max-models/tikzfigure
