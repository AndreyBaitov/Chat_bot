# -*- coding: utf-8 -*-
import logging

log = logging.getLogger('chat_bot')
log.setLevel(logging.INFO)
fh = logging.FileHandler("log/chat_bot.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# все возможные аттрибуты см https://docs.python.org/3.5/library/logging.html#logrecord-attributes
fh.setFormatter(formatter)
log.addHandler(fh)