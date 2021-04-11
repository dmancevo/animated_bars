music_tracks=`ls music | sort -R | python -c '''
import sys
tracks = ["music/"+sys.stdin.readline().replace("\n", "") for _ in range(4)]
print("concat:" + "|".join(tracks))
'''`

ffmpeg -i mov.mp4 -i $music_tracks -map 0:v -map 1:a -c:v copy -shortest mov2.mp4
mv mov2.mp4 ~/Downloads/
