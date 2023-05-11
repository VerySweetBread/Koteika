from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client['Koteika']
strings = db['strings']

ru = {
    "lang": "RU",
    "commands": {
        "HTiP": {
            "brief": "Кодирует текст в пикчу",
            "subcommand": "Опишите режим работы комманды!",
            "picNotExists": 'Мой великий взор не видит в этом сообщении то, чего мне надо. '
                            'Уходи и возвращайся  с изображением!',
            "w": {
                "brief": "Запись текста в пикчу",
                "textNotExists": "А что надо записать?"
            },
            "r": {
                "brief": "Чтение текста из пикчи"
            }
        },
        "hentai": {
            "brief": "Показывает взросло-деловой контент. Скука",
            "notFound": "Такого нет. Можешь воспользоваться `{}hentai help`",
            "notNSFW": "Тут низя"
        }
    }
}

en = {
    "lang": "EN",
    "commands": {
        "HTiP": {
            "brief": "Encodes text to the pic",
            "subcommand": "You didn't choose mode of the command!",
            "picNotExists": 'My great eye does not see what I need in this message. '
                            'Go away and come back with a picture!',
            "w": {
                "brief": "Writing text to the pic",
                "textNotExists": "What you need to write?"
            },
            "r": {
                "brief": "Reading text from the pic"
            }
        }
    }
}

strings.insert_many([ru, en])
