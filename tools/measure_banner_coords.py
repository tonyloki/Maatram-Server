from PIL import Image
import numpy as np

def measure_banner(img_path, is_ref=True):
    im = Image.open(img_path).convert('RGB')
    arr = np.array(im)
    # Check column x=400 down from y=40 to 350
    # Background outside banner is ~[250, 248, 245]. Banner is golden yellow ~[255, 230, 100] to [245, 184, 23]
    col = arr[:, 400, :]
    # Find rows where R > 230 and B < 200 (yellowish banner)
    is_yellow = (col[:, 0] > 230) & (col[:, 1] > 180) & (col[:, 2] < 210)
    indices = np.where(is_yellow)[0]
    if len(indices) > 0:
        start_y = indices[0]
        end_y = indices[-1]
        height = end_y - start_y
        print(f'{img_path} banner at x=400: start_y={start_y}, end_y={end_y}, height={height}')
    else:
        print(f'{img_path} banner not detected by color rule')

for name in ['Dashboard', 'Discover_Events', 'MyActivities', 'Leaderboard']:
    print(f'--- {name} ---')
    measure_banner(f'ui-Reference/{name}.jpeg')
    live_name = 'live_my_activity' if name == 'MyActivities' else f'live_{name.lower()}'
    measure_banner(f'docs/design/recreation/{live_name}_1536x1024.png')

