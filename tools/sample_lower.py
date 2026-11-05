from PIL import Image
import numpy as np

im = Image.open('ui-Reference/Dashboard.jpeg').convert('RGB')
arr = np.array(im)

print('=== Dashboard.jpeg y=500 to 1000 ===')
for y in range(500, 1000, 40):
    print(f'y={y:3d}: left_title x=350:{arr[y, 350].tolist()} left_card x=600:{arr[y, 600].tolist()} right_card x=1250:{arr[y, 1250].tolist()}')

