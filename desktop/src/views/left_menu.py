from aioqui.widgets import Label, Layout, ScrollArea, Button, Widget, Parent
from aioqui.widgets.custom import MenuButton, SearchBar
from aioqui.widgets.extensions import SplitterWidgetExt
from aioqui.qasyncio import asyncSlot
from aioqui.types import Icon
from aioqui import CONTEXT
from contextlib import suppress

from ..misc import ICONS, SIZES, API
from ..components import LabelExtended
from .. import stylesheets


class LeftMenu(SplitterWidgetExt, Widget):
    def __init__(self, parent: Parent):
        Widget.__init__(self, parent, self.__class__.__name__, stylesheet=stylesheets.left_menu.css +
                                                                          stylesheets.components.scroll +
                                                                          stylesheets.components.search)
        SplitterWidgetExt.__init__(self, 300, SIZES.LeftMenuMin, SIZES.LeftMenuMax, SplitterWidgetExt.Horizontal)

    async def init(self) -> 'LeftMenu':
        self.setLayout(await Layout.vertical().init(
            spacing=5, margins=(0, 10, 0, 10), alignment=Layout.Top,
            items=[
                await LabelExtended(self, 'LeftMenuItemsLabel').init(
                    text='Items', margins=(0, 0, 0, SIZES.LeftMenuTitlesMargin[3])
                ), Layout.Center,
                await MenuButton(self, 'AllItemsBtn').init(
                    icon=ICONS.HOME, text='All items', slot=CONTEXT.CentralItems.show_all
                ),
                await MenuButton(self, 'FavItemsBtn').init(
                    icon=Icon(ICONS.STAR.icon, ICONS.HOME.size), text='Favourite',
                    slot=CONTEXT.CentralItems.show_favourite
                ),
                await LabelExtended(self, 'LeftMenuCategoriesLabel').init(
                    text='Categories', margins=SIZES.LeftMenuTitlesMargin
                ), Layout.Center,
                SearchBar(self, visible=False),
                await Label(self, 'NoCategoriesLbl', False).init(
                    text='You don\'t have any categories yet', wrap=True,
                    sizes=Label.Sizes(vpolicy=Layout.Expanding, hpolicy=Layout.Expanding, alignment=Layout.HCenter)
                ), Layout.HCenter,
                await ScrollArea(self, 'CategoriesScrollArea', False).init(
                    hpolicy=ScrollArea.AlwaysOff, orientation=ScrollArea.Vertical, alignment=Layout.Top, spacing=5,
                    sizes=ScrollArea.Sizes(hpolicy=ScrollArea.Minimum)
                ),
                await Button(self, 'AddCategoryBtn').init(
                    text='Category', icon=ICONS.PLUS, events=Button.Events(on_click=CONTEXT.RightPagesCategory.show_create)
                )
            ]
        ))
        return self

    @asyncSlot()
    async def searchbar_textchanged(self):
        layout = self.CategoriesScrollArea.widget().layout()
        text = self.SearchBar.text()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            visible = True
            if widget.__class__.__name__ == 'LabelExtended':
                visible = widget.label.text()[0].lower() == text[0].lower() if len(text) else True
            elif widget.__class__.__name__ in 'MenuButton':
                visible = text.lower() in widget.text_lbl.text().lower()
            widget.setVisible(visible)
        with suppress(AttributeError):  # self.FavouriteLbl may not exist if none of items['is_favourite']
            self.FavouriteLbl.setVisible(not text)

    @asyncSlot()
    async def refresh_categories(self):
        layout = self.CategoriesScrollArea.widget().layout()
        layout.clear()
        categories = await API.get_categories()
        self.SearchBar.setVisible(bool(len(categories)))
        self.AllItemsBtn.AllItemsBtnTotalLbl.setText(str(sum([len(c['items']) for c in categories])))
        self.FavItemsBtn.FavItemsBtnTotalLbl.setText(str(sum([len([1 for i in c['items'] if i['is_favourite']]) for c in categories])))
        if not len(categories):
            self.CategoriesScrollArea.setVisible(False)
            return self.NoCategoriesLbl.setVisible(True)
        letters = []
        categories = sorted(categories, key=lambda c: (not c['is_favourite'], c['title'], c['description']))
        if any([category['is_favourite'] for category in categories]):
            layout.addWidget(await LabelExtended(self, 'FavouriteLbl').init(
                text='Favourite', margins=SIZES.LeftMenuLettersMargin
            ))
        for category in categories:
            if not category['is_favourite'] and (letter := category['title'][0]) not in letters:
                letters.append(letter)
                layout.addWidget(await LabelExtended(self, 'LetterLbl').init(
                    text=letter, margins=SIZES.LeftMenuLettersMargin
                ))
            layout.addWidget(await MenuButton(self).init(
                icon=Icon(category['icon'], SIZES.MenuBtnIcon), text=category['title'], total=len(category['items']),
                slot=lambda checked, _category=category: CONTEXT.RightPagesCategory.show_category(_category)
            ))
        await self.SearchBar.init(
            textchanged=self.searchbar_textchanged, placeholder='Search', stylesheet=stylesheets.components.search,
            items=[category['title'] for category in categories] + letters
        )
        self.NoCategoriesLbl.setVisible(False)
        self.CategoriesScrollArea.setVisible(True)
