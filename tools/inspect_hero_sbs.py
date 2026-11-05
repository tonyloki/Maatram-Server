from PIL import Image

mapping = {
    'Dashboard': 'live_dashboard_1536x1024.png',
    'Discover_Events': 'live_discover_events_1536x1024.png',
    'MyActivities': 'live_my_activity_1536x1024.png',
    'Leaderboard': 'live_leaderboard_1536x1024.png'
}

for name, live_file in mapping.items():
    ref_im = Image.open(f'ui-Reference/{name}.jpeg').convert('RGB')
    live_im = Image.open(f'docs/design/recreation/{live_file}').convert('RGB')
    
    # Crop hero region: x from 260 to 1500, y from 60 to 300
    ref_hero = ref_im.crop((260, 60, 1500, 300))
    live_hero = live_im.crop((260, 60, 1500, 300))
    
    # Create top-bottom comparison
    combined = Image.new('RGB', (1240, 480))
    combined.paste(ref_hero, (0, 0))
    combined.paste(live_hero, (0, 240))
    combined.save(f'docs/design/recreation/hero_comparison_{name}.png')
    print(f'Saved docs/design/recreation/hero_comparison_{name}.png')
