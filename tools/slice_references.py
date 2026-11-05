import os
from PIL import Image

def slice_and_describe(name):
    clean_name = name.replace('.jpeg', '')
    im = Image.open('ui-Reference/' + name)
    w, h = im.size
    print(f'*** {name} ({w}x{h}) ***')
    out_dir = f'docs/design/slices/{clean_name}'
    os.makedirs(out_dir, exist_ok=True)
    
    # 4 rows, 4 cols
    cw, ch = w // 4, h // 4
    for r in range(4):
        for c in range(4):
            box = (c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)
            crop = im.crop(box)
            crop.save(f'{out_dir}/r{r}_c{c}.png')
    print(f'Saved 16 slice crops for {clean_name}')

if __name__ == '__main__':
    for f in ['Dashboard.jpeg', 'Discover_Events.jpeg', 'Leaderboard.jpeg', 'MyActivities.jpeg', 'Profile_page.jpeg']:
        slice_and_describe(f)

