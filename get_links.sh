
links=$(python beatmap_link.py)
# echo "$links"
echo "$links" | wget -i -