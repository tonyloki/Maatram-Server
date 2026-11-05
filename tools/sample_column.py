from PIL import Image
import numpy as np

def sample_column(img_path, x=600):
    im = Image.open(img_path).convert('RGB')
    arr = np.array(im)
    print(f'=== {img_path} at x={x} ===')
    for y in range(0, 350, 20):
        print(f'y={y:3d}: RGB={arr[y, x].tolist()}')

sample_column('ui-Reference/Dashboard.jpeg', 600)
sample_column('docs/design/recreation/live_dashboard_1536x1024.png', 600)

