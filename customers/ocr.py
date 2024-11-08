# ocr.py

from draw import draw
draw_list = draw.split('\n')
import os

print(draw_list)

for d in draw_list:
    print(f'{d.strip()}')
    os.system(f'handprint -s microsoft {d.strip()} -e')
