from PIL import Image
import numpy as np

def analyze_crop(crop_name):
    im = Image.open(f'docs/design/recreation/{crop_name}.png').convert('RGB')
    w, h = im.size
    half_h = h // 2
    ref = im.crop((0, 0, w, half_h))
    live = im.crop((0, half_h, w, h))
    
    r_arr = np.array(ref, dtype=np.float32)
    l_arr = np.array(live, dtype=np.float32)
    diff = np.abs(r_arr - l_arr)
    sim = 100.0 - (np.mean(diff) / 255.0 * 100.0)
    print(f'=== {crop_name} ===: Similarity = {sim:.2f}%')
    
    # Let us sample reference vs live along key points
    # e.g. center
    print(f'  Ref center (x={w//2}, y={half_h//2}): {r_arr[half_h//2, w//2].astype(int).tolist()}')
    print(f'  Live center (x={w//2}, y={half_h//2}): {l_arr[half_h//2, w//2].astype(int).tolist()}')

for name in ['comp_header', 'comp_hero', 'comp_kpi', 'comp_lower']:
    analyze_crop(name)

