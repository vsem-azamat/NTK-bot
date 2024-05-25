import os
from typing import List
from decouple import config


# CONST VARIABLES
class Config:
    # >>>>>>>>>> TELEGRAM <<<<<<<<<< #
    BOT_TOKEN: str = str(config('BOT_TOKEN', cast=str))
    
    ID_NTK_BIG_CHAT: int = -1001684546093
    ID_NTK_SMALL_CHAT: int = -1001384533622
    ID_NTK_CHANNEL: int = -1001918057675
    SUPER_ADMINS: List[int] = [int(id_admin) for id_admin in str(config('SUPER_ADMINS', cast=str, default='')).split(',') if id_admin]

    # >>>>>>>>>> FILES <<<<<<<<<< #
    BAD_WORDS = []
    try:
        with open('bad_words.txt', 'r') as file:
            for line in file:
                word = line.strip()
                BAD_WORDS.append(word)
    except FileNotFoundError: pass 

    NTK_DATA_PATH= 'ntk_data.txt'
    if not os.path.exists(NTK_DATA_PATH):
        with open(NTK_DATA_PATH, 'w'): 
            pass


    # >>>>>>>>>> PARSERS <<<<<<<<<< #
    DELTA_TIME_FOR_RECIEVE_NTK: int = config('DELTA_TIME', cast=int, default=20)
    

cnfg = Config()

