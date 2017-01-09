#!/bin/bash

usage() {
  echo "Usage: $0 [-i INPUT_BASE] [-o OUTPUT_BASE]"
  echo "  e.g.: $0 -i nis -o test"
  echo "  By running such a command, the program will read in nis.%05d.ppm,"
  echo "  and output test.mp4."
  exit 1
}

while getopts ":i:o:" option; do
  case "${option}" in
    h)
      usage
      ;;
    i)
      INPUT_BASE=${OPTARG}
      ;;
    o)
      OUTPUT_BASE=${OPTARG}
      ;;
    *)
      echo "incorrect option flag detected."
      usage
      ;;
  esac
done

if [ $OPTIND -eq 1 ]; then
  echo "No arguments detected."
  usage
fi

# executable
ffmpeg -i ${INPUT_BASE}.%05d.ppm               \
       -vcodec libx264                         \
       -crf 25 -pix_fmt yuv420p                \
       -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
       ${OUTPUT_BASE}.mp4
