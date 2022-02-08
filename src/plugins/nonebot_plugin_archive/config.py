from pydantic import BaseSettings


class Config(BaseSettings):
    # Your Config Here

    class Config:
        extra = "ignore"
        entry_modify_success = [
            "词条编辑成功哟～",
            "Success～",
            "词条录入成功...",
            "词条录入ing...\nSuccess...",
        ]
        entry_remove_success = [
            "词条移除成功哟～",
            "Success～",
            "Succèss～",
            "词条移除成功...",
            "词条移除ing...\nSuccess...",
            "少女折寿中...\nSuccess!"
        ]
        entry_not_legal = [
            "嗯...待移除的词条不匹配呢...",
            "数据库中没有匹配的条目呢～",
            "请小伙伴确认词条名是否正确哦～",
            "参数不合法(๑>◡<๑)"
        ]