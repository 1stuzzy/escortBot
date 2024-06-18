from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: int = 5432

@dataclass
class TgBot:
    token: str
    main_bot_token: str
    admin_ids: list[int]

    guarantees_link: str
    reviews_link: str
    support_nick: str

@dataclass
class Miscellaneous:
    other_params: str = None

@dataclass
class Config:
    tg_bot: TgBot
    misc: Miscellaneous
    db: DbConfig = None

def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            main_bot_token=env.str("MAIN_BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            guarantees_link=env.str("GUARANTEES_LINK"),
            reviews_link=env.str("REVIEWS_LINK"),
            support_nick=env.str("SUPPORT_NICK")
        ),

        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('POSTGRES_PASSWORD'),
            user=env.str('POSTGRES_USER'),
            database=env.str('POSTGRES_DB'),
        ),

        misc=Miscellaneous()
    )
