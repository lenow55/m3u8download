# M3U8 playlist downloader

## Arguments

url: str - link for m3u8 playlist file

## Outputs

**./index.m3u8** - playlist file
**./tmp/\*ts** - ts video segments
**./tmp/filenames.txt** - file with list ts files for ffmpeg converter

## ffmpeg convertion

without gpu

```shell
ffmpeg -f concat -safe 0 -i filelist.txt -c:v libx264 \
  -c:a aac -strict experimental output.mp4
```

with gpu

```shell
ffmpeg -f concat -safe 0 -i filelist.txt -c:v h264_nvenc -preset fast \
  -profile:v high -level:v 4.2 -c:a aac output.mp4
```

without re encoding

```shell
mpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

with set screen resolution

```shell
ffmpeg -f concat -safe 0 -i filelist.txt -vf "scale=1280:720" \
  -c:v h264_nvenc -c:a aac output.mp4
```
