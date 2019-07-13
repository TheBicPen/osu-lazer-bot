beatmaps=$(python fetch_plays.py)
while IFS=';' read -ra ADDR; do
    for i in "${ADDR[@]}"; do
     echo "${ADDR[i]}"
    done
done <<< "$beatmaps"