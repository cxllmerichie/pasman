from aioqui.widgets import Layout, Widget, Splitter, Parent
from aioqui import CONTEXT

from .left_menu import LeftMenu
from .right_pages import RightPages
from .central_items import CentralItems
from ..components import Panel
from .. import stylesheets


class MainView(Widget):
    def __init__(self, parent: Parent):
        super().__init__(parent, self.__class__.__name__, stylesheet=stylesheets.view_main.css)

    async def init(self) -> 'MainView':
        central_items = await CentralItems(self).init()
        right_pages = await RightPages(self).init()
        left_menu = await LeftMenu(self).init()

        splitter = await Splitter(self, 'MainViewSplitter').init()
        splitter.addWidget(left_menu)
        splitter.addWidget(central_items, False)
        splitter.addWidget(right_pages)

        self.setLayout(await Layout.vertical().init(
            items=[
                await Panel(self).init(

                ), Layout.Top,
                splitter
            ]
        ))
        await CONTEXT.RightPagesCategory.show_create()
        left_menu.expand()
        right_pages.shrink()
        return self
