RICH_TEXT = "rich_text"
URL = "url"
RELATION = "relation"
NUMBER = "number"
DATE = "date"
FILES = "files"
STATUS = "status"
TITLE = "title"
SELECT = "select"
CHECKBOX = "checkbox"
MULTI_SELECT = "multi_select"

book_properties_type_dict = {
    "标题": TITLE,
    "Description": RICH_TEXT,
    "音频": RICH_TEXT,
    "Eid": RICH_TEXT,
    "链接": URL,
    "发布时间": DATE,
    "时长": NUMBER,
    "时间戳": NUMBER,
    "状态": STATUS,
    "Podcast": RELATION,
        "喜欢": CHECKBOX,
}

TAG_ICON_URL = "https://www.notion.so/icons/hourglass_gray.svg"


movie_properties_type_dict = {
    "播客": TITLE,
    "Brief": RICH_TEXT,
    "Description": RICH_TEXT,
    "Pid": RICH_TEXT,
    "作者": RELATION,
    "全部": RELATION,
    "最后更新时间": DATE,
    "链接": URL,
    "收听时长": NUMBER,
}
{
    "标题": {
        "title": [
            {
                "type": "text",
                "text": {"content": "Vol.224 金色梦乡：你知道人最强大的武器是什么吗？"},
            }
        ]
    },
    "Description": {
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": "本期节目我们一起读小说《金色梦乡》，作者伊坂幸太郎。\n《金色梦乡》出版于2007年，讲述了平凡的前送货员青柳雅春被突然当作刺杀首相的凶手，遭到政府通缉，同时被媒体炒作网暴，成为“十恶不赦的罪人”，因此唯一的出路只有拼命逃跑，在惊险的跑路中，与警方短兵相接，也得到情义相挺，莫名其妙的命运捉弄中，他能否顺利逃出重围？这个故事的灵感来自于真实历史事件“肯尼迪遇刺案”。\n伊坂幸太郎（1971-），日本作家。2000年以《奥杜邦的祈祷》获得“新潮推理俱乐部奖”，由此跻身文坛，曾五度入围“直木奖”，是公认的“文坛才子”。\n你会听到：\n1、什么是套路？\n2、看“原著”的意义是什么？\n3、《金色梦乡》和伊坂幸太郎简介。\n4、如何理解书中关于美国、摇滚、披头士、刺杀总统等意象？\n5、精彩片段分享。\n6、伊坂幸太郎的作品为什么畅销？怎么理解“人类最后的武器是信任”和标题《金色梦乡》？\n片头曲：靛厂\n片尾曲：Golden Slumbers (Remastered 2009)\n主播：大壹 / 超哥 / 星光"
                },
            }
        ]
    },
    "时间戳": {"number": 1712012400},
    "发布时间": {
        "date": {"start": "2024-04-02 07:00:00", "time_zone": "Asia/Shanghai"}
    },
    "音频": {
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": "https://jt.ximalaya.com//GKwRINsJ3BQ4An6aiQK-6Qkb-aacv2-48K.m4a?channel=rss&album_id=29887212&track_id=718781905&uid=68693381&jt=https://audio.xmcdn.com/storages/e11f-audiofreehighqps/0B/16/GKwRINsJ3BQ4An6aiQK-6Qkb-aacv2-48K.m4a"
                },
            }
        ]
    },
    "Eid": {
        "rich_text": [{"type": "text", "text": {"content": "660b3dad1c3c7de44a82f773"}}]
    },
    "时长": {"number": 5169},
    "Podcast": {"relation": [{"id": "87723a05-dd9a-494d-a934-9ff4140fcb21"}]},
    "链接": {"url": "hhttps://www.xiaoyuzhoufm.com/episode/660b3dad1c3c7de44a82f773"},
    "状态": {"status": {"name": "在听"}},
}
