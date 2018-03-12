#!/usr/bin/env sh
set -x -e -o pipefail

git config user.name IGitt-bot
git config user.email support@gitmate.io
git tag -a $(cat IGitt/VERSION) -m $(cat IGitt/VERSION)
git push --tags --quiet https://oauth2:${RELEASE_TOKEN}@gitlab.com/${CI_PROJECT_PATH}.git
