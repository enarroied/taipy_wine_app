import taipy.gui.builder as tgb

from callbacks import on_change_region

with tgb.Page() as by_region_page:
    with tgb.layout("1 2"):
        tgb.selector(
            "{selected_region}",
            lov="{list_of_regions}",
            on_change=on_change_region,
            dropdown=True,
            label="Choose Region",
        )
        tgb.text("# Wine production | **by Region**", mode="md")
    tgb.text("## Charts:", mode="md")

    with tgb.layout("1 1"):
        tgb.chart(
            "{df_region_red}",
            properties="{property_plot_red}",
            layout="{plot_chart_layout}",
        )
        tgb.chart(
            "{df_region_white}",
            properties="{property_plot_white}",
            layout="{plot_chart_layout}",
        )
