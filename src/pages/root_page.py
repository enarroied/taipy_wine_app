import taipy.gui.builder as tgb

with tgb.Page() as root_page:
    with tgb.layout("5 1"):
        tgb.navbar()
        tgb.toggle(theme=True)
