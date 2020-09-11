import unittest

import fetch_plays as fp

class TestFP(unittest.TestCase):
    def test_no_map(self):
        post = """| Player                                                                | Rank                  | pp     | Accuracy | Playcount |
            :-:|:-:|:-:|:-:|:-:
            | [Umbre](https://osu.ppy.sh/u/2766034 "Previously known as 'oharryo'") | #28&nbsp;(#3&nbsp;DE) | 15,359 | 99.42%   | 233,402   |

            YouTube links: [[1]](https://youtu.be/cTrZ6iBvngs "'[7.75⭐Live] Umbre | BABYMETAL - Road of Resistance [Determined] 99.83% {#2 816pp FC} - osu!' by 'cpol'") [[2]](https://youtu.be/6YrFyawPLHM "'osu! | Umbre | BABYMETAL - Road of Resistance [Determined] 7.75⭐ 99.83% FC | 816pp #2' by 'Circle People'")

            ***

            ^(kirito is legit – )[^Source](https://github.com/christopher-dG/osu-bot)^( | )[^Developer](https://reddit.com/u/PM_ME_DOG_PICS_PLS) [&nbsp;](http://x "Beatmap 'BABYMETAL - Road of Resistance  [Determined]': Not found")
        """
        play = fp.PlayDetails(post, "")
        self.assertEqual(play.comment_text, post)
        self.assertEqual(play.player_name, "Umbre")
        self.assertEqual(play.player_link, "https://osu.ppy.sh/u/2766034")
        self.assertEqual(play.post_title, "")
        self.assertIsNone(play.top_play_of_player)
        self.assertIsNone(play.beatmap_name)
        self.assertIsNone(play.beatmap_link)
        self.assertIsNone(play.beatmapset_download)
        self.assertIsNone(play.mapper_link)
        self.assertIsNone(play.mods_bitmask)

    def test_map_and_player(self):
        post = """#### [Chopin - Revolutionary Etude [Prestissimissimo]](https://osu.ppy.sh/b/1142884?m=0) [(&#x2b07;)](https://osu.ppy.sh/d/539300 "Download this beatmap") by [Louis Cyphre](https://osu.ppy.sh/u/186243) || osu!standard
            **#1: [goink](https://osu.ppy.sh/u/1920049 "8,530pp - rank #3,019 (#512 US) - 87.02% accuracy - 74,326 playcount") (+SOTD - 90.12%) || 681x max combo || Loved (2018) || 62,964 plays**

            |       | CS  | AR | OD | HP | SR    | BPM | Length | pp (89.24% &#124; 95% &#124; 98% &#124; 99% &#124; 100%) |
            :-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:
            | NoMod | 4   | 10 | 9  | 8  | 9.66  | 145 | 01:21  | 800 &#124; 841 &#124; 882 &#124; 904 &#124; 932          |
            | +HRNF | 5.2 | 10 | 10 | 10 | 10.36 | 145 | 01:21  | 898 &#124; 946 &#124; 999 &#124; 1,027 &#124; 1,064      |

            | Player                                                                    | Rank                 | pp     | Accuracy | Playstyle | Playcount |
            :-:|:-:|:-:|:-:|:-:|:-:
            | [Vaxei](https://osu.ppy.sh/u/4787150 "Previously known as 'Donkey Kong'") | #4&nbsp;(#1&nbsp;US) | 17,429 | 98.68%   | TB+KB     | 145,283   |

            ***

            ^(nice pass ecks dee – )[^Source](https://github.com/christopher-dG/osu-bot)^( | )[^Developer](https://reddit.com/u/PM_ME_DOG_PICS_PLS) [&nbsp;](http://x "Beatmap: Found in events
            .osu: Downloaded from S3")
            """
        play = fp.PlayDetails(post, "")
        self.assertEqual(play.comment_text, post)
        self.assertEqual(play.player_name, "Vaxei")
        self.assertEqual(play.player_link, "https://osu.ppy.sh/u/4787150")
        self.assertEqual(play.post_title, "")
        self.assertIsNone(play.top_play_of_player)
        self.assertEqual(play.beatmap_name, "Chopin - Revolutionary Etude [Prestissimissimo]")
        self.assertEqual(play.beatmap_link, "https://osu.ppy.sh/b/1142884?m=0")
        self.assertEqual(play.beatmapset_download, "https://osu.ppy.sh/d/539300")
        self.assertEqual(play.mapper_link, "https://osu.ppy.sh/u/186243")
        self.assertEqual(play.mapper_name, "Louis Cyphre")
        self.assertEqual(play.mods_string, "HRNF")
        self.assertEqual(play.mods_bitmask, 17)
        self.assertEqual(play.length, 81)


    def test_length_change_mod(self):
        post = """#### [07th Expansion - rog-unlimitation [AngelHoney]](https://osu.ppy.sh/b/116128?m=0) [(&#x2b07;)](https://osu.ppy.sh/d/28751 "Download this beatmap") by [AngelHoney](https://osu.ppy.sh/u/104401) || osu!standard
        **#1: [aetrna](https://osu.ppy.sh/u/6447454 "16,571pp - rank #10 (#2 CA) - 97.14% accuracy - 131,150 playcount") (+HDDT - 96.25% - 1,121pp) || 850x max combo || Ranked (2012) || 2,065,166 plays**

        |       | CS | AR | OD  | HP | SR   | BPM | Length | pp (85.17% &#124; 95% &#124; 98% &#124; 99% &#124; 100%) |
        :-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:
        | NoMod | 3  | 10 | 7   | 7  | 6.35 | 220 | 02:16  | 220 &#124; 245 &#124; 262 &#124; 272 &#124; 285          |
        | +DT   | 3  | 11 | 9.1 | 7  | 9.77 | 330 | 01:31  | 954 &#124; 1,057 &#124; 1,113 &#124; 1,140 &#124; 1,175  |

        | Player                                                                            | Rank                          | pp    | Accuracy | Playstyle | Playcount | Top Play                                                                                                                                                               |
        :-:|:-:|:-:|:-:|:-:|:-:|:-:
        | [XxfortniteproxX](https://osu.ppy.sh/u/11858088 "Previously known as 'lokikaos'") | #14,867&nbsp;(#2,551&nbsp;US) | 6,402 | 93.60%   | TB+KB     | 77,575    | [07th&nbsp;Expansion&nbsp;&#x2011;&nbsp;rog&#x2011;unlimitation&nbsp;[AngelHoney]](https://osu.ppy.sh/b/116128?m=0) +DT&nbsp;&#124;&nbsp;85.17%&nbsp;&#124;&nbsp;681pp |

        ***

        ^(nice pass ecks dee – )[^Source](https://github.com/christopher-dG/osu-bot)^( | )[^Developer](https://reddit.com/u/PM_ME_DOG_PICS_PLS) [&nbsp;](http://x "Beatmap: Found in best
        .osu: Downloaded from S3")
        """
        title = "XxfortniteproxX | 07th Expansion - rog-unlimitation [AngelHoney] +DT 85.17% 0 MISS! (9.77*) | 681pp | 954pp for FC | 557/850x | His new top play, Skipped 400, 500"
        play = fp.PlayDetails(post, title)
        self.assertEqual(play.post_title, title)
        self.assertEqual(play.length, 91)
        self.assertEqual(play.player_name, "XxfortniteproxX")
        # self.assertEqual(play.top_play_of_player, "[07th&nbsp;Expansion&nbsp;&#x2011;&nbsp;rog&#x2011;unlimitation&nbsp;[AngelHoney]](https://osu.ppy.sh/b/116128?m=0) +DT&nbsp;&#124;&nbsp;85.17%&nbsp;&#124;&nbsp;681pp")
        self.assertIsNone(play.top_play_of_player)
        self.assertEqual(play.player_link, "https://osu.ppy.sh/u/11858088")
        self.assertEqual(play.mapper_name, "AngelHoney")
        self.assertEqual(play.mapper_link, "https://osu.ppy.sh/u/104401")
        self.assertEqual(play.beatmap_link, "https://osu.ppy.sh/b/116128?m=0")
        self.assertEqual(play.beatmapset_download, "https://osu.ppy.sh/d/28751")
        # self.assertEqual(play.top_on_map, "aetrna")
        self.assertIsNone(play.top_on_map)


    def test_catch_post(self):
        post = """#### [xi - FREEDOM DiVE [Another]](https://osu.ppy.sh/b/126645?m=2) [(&#x2b07;)](https://osu.ppy.sh/d/39804 "Download this beatmap") by [Nakagawa-Kanon](https://osu.ppy.sh/u/87065 "20 ranked, 0 qualified, 2 loved, 31 unranked") || osu!catch
        **#1: [T s u m i](https://osu.ppy.sh/u/4080520 "7,703pp - rank #537 (#45 KR) - 99.78% accuracy - 98,978 playcount") (+HDHR - 99.96% - 336pp) || 1,943x max combo || Ranked (2012) || 7,348,090 plays**

        |       | CS | AR | OD | HP | SR   | BPM | Length | pp (95% &#124; 98% &#124; 99% &#124; 100%) |
        :-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:
        | NoMod | 4  | 9  | 8  | 7  | 4.38 | 222 | 04:18  | 180 &#124; 213 &#124; 225 &#124; 238       |
        | +FL   | 4  | 9  | 8  | 7  | 4.38 | 222 | 04:18  | 293 &#124; 348 &#124; 368 &#124; 389       |

        | Player                                                                | Rank                    | pp    | Accuracy | Playcount | Top Play                                                                                                                                                                                                                       |
        :-:|:-:|:-:|:-:|:-:|:-:
        | [Morsay](https://osu.ppy.sh/u/4223607 "Previously known as 'Hibari'") | #244&nbsp;(#18&nbsp;FR) | 9,770 | 99.58%   | 163,714   | [Hitsuji&nbsp;to&nbsp;Ojisan&nbsp;&#x2011;&nbsp;XENO&nbsp;[Spec's&nbsp;Overdose]](https://osu.ppy.sh/b/663001?m=2 "SR6.92 - CS5.2 - AR10 - OD10 - HP10 - 186BPM - 02:28") +HRFL&nbsp;&#124;&nbsp;99.10%&nbsp;&#124;&nbsp;678pp |

        ***

        ^(can just shut up – )[^Source](https://github.com/christopher-dG/osu-bot)^( | )[^Developer](https://reddit.com/u/PM_ME_DOG_PICS_PLS)^( | )^(osu!catch pp is experimental) [&nbsp;](http://x "Beatmap: Found in events
        Max combo: Found via API
        .osu: Downloaded from S3")
        """
        play = fp.PlayDetails(post, "title")
        self.assertEqual(play.length, 258)
        self.assertEqual(play.player_name, "Morsay")
        self.assertEqual(play.player_link, "https://osu.ppy.sh/u/4223607")
        self.assertEqual(play.mapper_name, "Nakagawa-Kanon")
        self.assertEqual(play.mapper_link, "https://osu.ppy.sh/u/87065")
        self.assertEqual(play.beatmap_link, "https://osu.ppy.sh/b/126645?m=2")
        self.assertEqual(play.beatmapset_download, "https://osu.ppy.sh/d/39804")

    def test_loved_post(self):
        # post is loved. mapper renamed. TD mod in #1. player renamed.
        post = """#### [DatManOvaDer - Busta Rhymes Goes To The Wii Shop Channel [oof]](https://osu.ppy.sh/b/1681634?m=0) [(&#x2b07;)](https://osu.ppy.sh/d/801074 "Download this beatmap") by [Fowwo](https://osu.ppy.sh/u/4547551 "Renamed to 'fowwo': 0 ranked, 0 qualified, 1 loved, 55 unranked") || osu!standard
**#1: [goink](https://osu.ppy.sh/u/1920049 "8,531pp - rank #3,074 (#521 US) - 87.03% accuracy - 74,988 playcount") (+TD - 88.72%) || 504x max combo || Loved (2019) || 397,431 plays**

| CS | AR | OD | HP | SR   | BPM | Length | pp (95% &#124; 96.18% &#124; 98% &#124; 99% &#124; 100%) |
:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:
| 4  | 10 | 10 | 6  | 8.37 | 150 | 00:59  | 589 &#124; 605 &#124; 645 &#124; 670 &#124; 708          |

| Player                                                                        | Rank                  | pp     | Accuracy | Playstyle | Playcount | Top Play                                                                                                                                                                                                            |
:-:|:-:|:-:|:-:|:-:|:-:|:-:
| [badeu](https://osu.ppy.sh/u/1473890 "Previously known as 'badeatudorpetre'") | #17&nbsp;(#1&nbsp;RO) | 16,254 | 97.48%   | TB+KB     | 102,140   | [Turbo&nbsp;&#x2011;&nbsp;PADORU&nbsp;/&nbsp;PADORU&nbsp;[Gift]](https://osu.ppy.sh/b/2245774?m=0 "SR9.37 - CS5.2 - AR11 - OD11.1 - HP8.7 - 285BPM - 00:21") +HDDTHR&nbsp;&#124;&nbsp;98.19%&nbsp;&#124;&nbsp;989pp |

***

^(play more – )[^Source](https://github.com/christopher-dG/osu-bot)^( | )[^Developer](https://reddit.com/u/PM_ME_DOG_PICS_PLS) [&nbsp;](http://x "Beatmap: Found in events
.osu: Downloaded from S3")
            """
        play = fp.PlayDetails(post, "title")
        self.assertEqual(play.length, 59)
        self.assertEqual(play.player_name, "badeu")
        self.assertEqual(play.player_link, "https://osu.ppy.sh/u/1473890")
        self.assertEqual(play.mapper_name, "Fowwo")
        self.assertEqual(play.mapper_link, "https://osu.ppy.sh/u/4547551")
        self.assertEqual(play.beatmap_link, "https://osu.ppy.sh/b/1681634?m=0")
        self.assertEqual(play.beatmapset_download, "https://osu.ppy.sh/d/801074")

        




if __name__ == '__main__':
    unittest.main()