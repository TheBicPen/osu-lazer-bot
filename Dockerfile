FROM mcr.microsoft.com/dotnet/core/sdk:3.1 as build

WORKDIR /src

# Update aptitude with new repo
RUN apt-get update

# install software
RUN apt-get install -y git

# Get osu and lazer-bot repos to working state
COPY ./patches ./patches
RUN git clone https://github.com/ppy/osu.git \
    && cd ./osu \
    && git checkout fb5a54d2422171d8f2cb40ee1cb4b9b96dabc4f7 \
    && git apply ../patches/*.patch

# compile osu
RUN cd /src/osu/osu.Desktop \
    && dotnet restore \
    && dotnet publish -c Release -o /app

FROM mcr.microsoft.com/dotnet/core/runtime:3.1
WORKDIR /app
COPY --from=build /app ./build
COPY . ./bot
RUN apt-get update \
    && apt-get install -y git xvfb ffmpeg python3 python3-pip

# set env vars
RUN cd /app/bot \
    && sh env_to_file.sh \
    && echo "/app/rec" > creds/recording_folder.txt \
    && echo "/app/build/osu!" > creds/osu_path.txt

RUN pip3 install -r bot/requirements.txt

# X server setup
ENV DISPLAY=:99
ENV XDG_RUNTIME_DIR=/app/tmp
RUN Xvfb :99 -screen 0 1280x720x8 &
ENTRYPOINT [ "/app/build/osu!" ]

