#!/bin/bash

# 元数据文件
metadata_file="metadata.txt"

# 检查元数据文件是否存在
if [ ! -f "$metadata_file" ]; then
    echo "元数据文件 $metadata_file 不存在"
    exit 1
fi

# 输出目录
output_dir="fixed_videos"
mkdir -p "$output_dir"

# 遍历所有视频文件
for video_file in *.mp4; do
    if [ -f "$video_file" ]; then
        output_file="$output_dir/${video_file%.*}_fixed.mp4"
        ffmpeg -i "$video_file" -i "$metadata_file" -map_metadata 1 -codec copy "$output_file"
        echo "已处理: $video_file -> $output_file"
    else
        echo "未找到视频文件: $video_file"
    fi
done

echo "所有视频处理完成。"
