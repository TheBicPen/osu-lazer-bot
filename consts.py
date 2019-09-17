import re

# Regex stuff
title_re = re.compile(".+[\|丨].+-.+\[.+\]")
map_re = re.compile(".+[\|丨](.+-.+\[.+\])")
map_pieces_re = re.compile("(.+) - (.+?)\[(.+)\]")
map_double_brackets_re = re.compile("(.+) - (.+?\[.+?\]) \[(.+)\]")
player_re = re.compile("(.+)[\|丨].+-.+\[.+\]")
event_re = re.compile("<a href=[\"']/b/\d+\?m=\d[\"']>(.+ - .+ \[.+\])</a> \((.+)\)")  # noqa
acc_re = re.compile("(\d{1,3}(?:[\.,]\d+)?)%")
tail_re = re.compile(".+[\|丨].+-.+\[.+\](.+)")
scorev2_re = re.compile("SV2|SCOREV2")
paren_re = re.compile("\((.+?)\)")
bracket_re = re.compile("\[(.+?)\]")
mapper_id_re = re.compile("Creator:</td><td class=[\"']colour[\"']><a href=[\"']/u/(\d+)")  # noqa
old_username_re = re.compile("<div class=[\"']profile-username[\"']\s+title=[\"']Previously known as (.+?)[\"']>")  # noqa
combo_re = re.compile("Max Combo</strong></td><td ?>([0-9]+)</td>")
misses_re = re.compile("<strong>Misses</strong></td><td ?>([0-9]+)</td>")
mania_misses_re = re.compile("<strong>100 / 50 / Misses</strong></td><td ?>\d+ / \d+ / ([0-9]+)</td>")  # noqa
playstyle_m_re = re.compile("<div class=[\"']playstyle mouse using[\"']></div>")  # noqa
playstyle_kb_re = re.compile("<div class=[\"']playstyle keyboard using[\"']></div>")  # noqa
playstyle_tb_re = re.compile("<div class=[\"']playstyle tablet using[\"']></div>")  # noqa
playstyle_td_re = re.compile("<div class=[\"']playstyle touch using[\"']></div>")  # noqa
osu_file_begin_re = re.compile("\A.*osu file format")