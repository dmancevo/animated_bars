for url in `wget -O- https://en.wikipedia.org/wiki/Gallery_of_sovereign_state_flags | grep -o //upload.wikimedia.org/wikipedia/commons/thumb/[a-z0-9]*/[a-z0-9]*/Flag_of_[_%0-9a-zA-Z]*.svg/[0-9][0-9]*px-Flag_of_[_%0-9a-zA-Z]*.svg.png | sort | uniq`
do
    file_name=`echo $url | grep -o Flag_of_[_%0-9a-zA-Z]*.svg.png | sed s/Flag_of_//g | sed s/\.svg//g`
    echo $file_name
    if [ -f $file_name ]; then
        continue
    else
        wget "https:$url" -o /dev/null -O $file_name
    fi
done
