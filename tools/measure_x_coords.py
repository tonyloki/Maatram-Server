from PIL import Image
import numpy as np

im = Image.open('ui-Reference/Dashboard.jpeg').convert('RGB')
arr = np.array(im)

# Let us check horizontal line y=200
# Background is warm cream. Look for the white card of the sidebar
print('=== Horizontal line y=200 in Dashboard.jpeg ===')
row = arr[200, :, :]
# Find where the sidebar card is (it is white or near white, with border)
# Find where the main hero banner is (golden yellow R>240, G>220)
for x in range(0, 1536, 30):
    rgb = row[x].tolist()
    print(f'x={x:4d}: RGB={rgb}')

