#!/bin/sh
export OSU_LAZER_BOT_OSU_CREDENTIALS="$(cat creds/osu_credentials.txt)"
export OSU_LAZER_BOT_OSU_PATH="$(cat creds/osu_path.txt)"
export OSU_LAZER_BOT_OSU_TOKEN="$(cat creds/osu_token.txt)"
export OSU_LAZER_BOT_RECORDING_FOLDER="$(cat creds/recording_folder.txt)"
export OSU_LAZER_BOT_REDDIT_TOKEN="$(cat creds/reddit_token.txt)"
export OSU_LAZER_BOT_YOUTUBE_CLIENT_SECRETS="$(cat creds/youtube_client_secrets.json)"
export OSU_LAZER_BOT_YOUTUBE_OAUTH2="$(cat creds/youtube_oauth2.json)"
export OSU_LAZER_BOT_YOUTUBE_TOKEN="$(cat creds/youtube_token.txt)"