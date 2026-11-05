from PIL import Image

im = Image.open('docs/design/recreation/compare_dashboard_sbs.png')
w, h = im.size
# Left half is Reference (0..1536), Right half is Live (1536..3072)
ref = im.crop((0, 0, 1536, h))
live = im.crop((1536, 0, 3072, h))

# Let's save 5 focused comparison crops:
# 1. Sidebar comparison
ref_side = ref.crop((0, 0, 270, 1024))
live_side = live.crop((0, 0, 270, 1024))
side_comp = Image.new('RGB', (540, 1024))
side_comp.paste(ref_side, (0, 0))
side_comp.paste(live_side, (270, 0))
side_comp.save('docs/design/recreation/comp_sidebar.png')

# 2. Header comparison
ref_head = ref.crop((270, 0, 1536, 80))
live_head = live.crop((270, 0, 1536, 80))
head_comp = Image.new('RGB', (1266, 160))
head_comp.paste(ref_head, (0, 0))
head_comp.paste(live_head, (0, 80))
head_comp.save('docs/design/recreation/comp_header.png')

# 3. Hero banner comparison
ref_hero = ref.crop((270, 80, 1536, 310))
live_hero = live.crop((270, 80, 1536, 310))
hero_comp = Image.new('RGB', (1266, 460))
hero_comp.paste(ref_hero, (0, 0))
hero_comp.paste(live_hero, (0, 230))
hero_comp.save('docs/design/recreation/comp_hero.png')

# 4. KPI row comparison
ref_kpi = ref.crop((270, 310, 1536, 510))
live_kpi = live.crop((270, 310, 1536, 510))
kpi_comp = Image.new('RGB', (1266, 400))
kpi_comp.paste(ref_kpi, (0, 0))
kpi_comp.paste(live_kpi, (0, 200))
kpi_comp.save('docs/design/recreation/comp_kpi.png')

# 5. Lower section comparison
ref_lower = ref.crop((270, 510, 1536, 1024))
live_lower = live.crop((270, 510, 1536, 1024))
lower_comp = Image.new('RGB', (1266, 1028))
lower_comp.paste(ref_lower, (0, 0))
lower_comp.paste(live_lower, (0, 514))
lower_comp.save('docs/design/recreation/comp_lower.png')

print('All 5 region comparison crops saved!')

