from taipy.gui import Gui

from pages.all_regions import *
from pages.by_region import *

# Toggle theme: switch dark/light mode
root_md = """
<|toggle|theme|>
<center>\n<|navbar|>\n</center>
"""

stylekit = {
    "color-primary": "#CC3333",
    "color-secondary": "#E0C095",
    "color-background-light": "#F7E7CE",
    "color-background-dark": "#E0C095",
}

pages = {"/": root_md, "all_regions": all_regions_md, "by_region": by_region_md}


gui_multi_pages = Gui(pages=pages)

if __name__ == "__main__":
    gui_multi_pages.run(
        use_reloader=True,
        title="Wine 🍷 production by Region and Year",
        dark_mode=False,
        stylekit=stylekit,
    )
