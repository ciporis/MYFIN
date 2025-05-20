from enum import Enum

class Operations(Enum):
    INCOME = "Приход"
    OUTCOME = "Расход"
    TRANSFER_TO = "Исходящий перевод"
    TRANSFER_FROM = "Входящий перевод"