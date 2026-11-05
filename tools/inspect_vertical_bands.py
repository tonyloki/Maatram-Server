from PIL import Image
import numpy as np

def inspect_page_diffs(ref_path, live_path, page_name):
    ref = Image.open(ref_path).convert('RGB')
    live = Image.open(live_path).convert('RGB')
    
    print(f'=== {page_name} ===')
    print(f'Ref size: {ref.size}, Live size: {live.size}')
    
    # Resize live to ref size if different
    if live.size != ref.size:
        live = live.resize(ref.size, Image.Resampling.LANCZOS)
    
    r_arr = np.array(ref, dtype=np.float32)
    l_arr = np.array(live, dtype=np.float32)
    diff = np.abs(r_arr - l_arr)
    mean_diff = np.mean(diff)
    similarity = 100.0 - (mean_diff / 255.0 * 100.0)
    print(f'Global similarity: {similarity:.2f}%')
    
    # Check vertical bands (every 100px from top to bottom)
    for y in range(0, ref.height, 100):
        y_end = min(y + 100, ref.height)
        band_diff = np.mean(diff[y:y_end, :, :])
        band_sim = 100.0 - (band_diff / 255.0 * 100.0)
        print(f'  y={y:4d}..{y_end:4d}: similarity={band_sim:.2f}%')

if __name__ == '__main__':
    inspect_page_diffs('ui-Reference/Dashboard.jpeg', 'docs/design/recreation/live_dashboard_1536x1024.png', 'Dashboard')
    inspect_page_diffs('ui-Reference/Discover_Events.jpeg', 'docs/design/recreation/live_discover_events_1536x1024.png', 'Discover Events')
    inspect_page_diffs('ui-Reference/MyActivities.jpeg', 'docs/design/recreation/live_my_activity_1536x1024.png', 'My Activities')
    inspect_page_diffs('ui-Reference/Leaderboard.jpeg', 'docs/design/recreation/live_leaderboard_1536x1024.png', 'Leaderboard')
    inspect_page_diffs('ui-Reference/Profile_page.jpeg', 'docs/design/recreation/live_profile_1600x900.png', 'Profile Page')

