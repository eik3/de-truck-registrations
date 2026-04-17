#!/usr/bin/env bash
#
# Entrypoint script for building and running the de-truck-registrations Docker
# container. Run ./do without arguments to see available commands.
#
# Conventions:
#   - Public commands: plain lowercase function names, optionally hyphenated
#     (e.g. build, run, docker-image-build). These are automatically discoverable
#     via ./do help and callable as ./do <command>.
#   - Internal helpers: functions prefixed with an underscore (e.g. _my_helper).
#     These are not listed in help and cannot be called via ./do.
#   - Each public function must contain at least one # DOCUMENTATION: comment
#     immediately inside its body. This is what appears in ./do help.
#     Multi-line documentation uses one # DOCUMENTATION: prefix per line.

set -o errexit
set -o errtrace
set -o nounset
set -o pipefail

IMAGE_NAME="de-truck-registrations"
IMAGE_TAG="latest"

function build() {
  # DOCUMENTATION: Build the Docker image

  echo "Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}..."
  docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
  echo "Docker image built successfully."
}

function run() {
  # DOCUMENTATION: Run the application in a Docker container

  local output_dir="./output"
  local output_file="${output_dir}/neuzulassungen_sattelzugmaschinen.png"

  echo "Running Docker container from image ${IMAGE_NAME}:${IMAGE_TAG}..."
  mkdir -p "${output_dir}"
  docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" > "${output_file}"
  echo "Container finished execution. Graph saved as '${output_file}'."
}

function help() {
  # DOCUMENTATION: Print available commands and their documentation

  echo "Usage: ./do <command>"
  echo
  echo "Commands:"
  echo
  egrep '^(function [a-z]|  # DOCUMENTATION:)' "$0" \
		| sed -e 's/function //' -e 's/() {//' -e '/^main$/d' -e 's/# DOCUMENTATION: //'
}

function main() {
  [[ -z ${1:-} ]] && help && exit

  local command=$1 && shift
  local -a public_commands
  mapfile -t public_commands < <(help | grep '^[a-z]')

  local cmd
  for cmd in "${public_commands[@]}"; do
    if [[ "$cmd" == "$command" ]]; then
      $command "$@"
      return
    fi
  done

  echo "./do: unknown command '${command}'" >&2
  echo "Try './do help' for a list of available commands." >&2
  exit 1
}

main "$@"
