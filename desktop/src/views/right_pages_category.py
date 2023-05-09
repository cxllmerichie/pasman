from qcontextapi.widgets import Button, LineInput, Layout, Label, TextInput, Spacer, Frame
from qcontextapi.customs import FavouriteButton, ImageButton, ErrorLabel
from qcontextapi.misc import Icon
from qcontextapi import CONTEXT
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.QtCore import pyqtSlot
from typing import Any

from ..misc import ICONS, API, utils, PATHS
from .. import stylesheets


class RightPagesCategory(Frame):
    def __init__(self, parent: QWidget):
        super().__init__(parent, self.__class__.__name__, stylesheet=stylesheets.right_pages_category.css +
                                                                     stylesheets.components.favourite_button +
                                                                     stylesheets.components.image_button)

    def init(self) -> 'RightPagesCategory':
        self.setLayout(Layout.vertical().init(
            spacing=20, margins=(25, 10, 25, 20),
            items=[
                Layout.horizontal().init(
                    margins=(0, 0, 0, 20),
                    items=[
                        FavouriteButton(self).init(
                            pre_slot=self.toggle_favourite
                        ), Layout.Left,
                        Button(self, 'EditBtn', False).init(
                            icon=ICONS.EDIT.adjusted(size=(30, 30)), slot=self.execute_edit
                        ),
                        Button(self, 'DeleteBtn', False).init(
                            icon=ICONS.TRASH.adjusted(size=(30, 30)), slot=self.execute_delete
                        ),
                        Button(self, 'CloseBtn').init(
                            icon=ICONS.CROSS.adjusted(size=(30, 30)), slot=CONTEXT.RightPages.shrink
                        ), Layout.Right
                    ]
                ),
                ImageButton(self).init(
                    icon=ICONS.CATEGORY, directory=PATHS.ICONS
                ), Layout.TopCenter,
                LineInput(self, 'TitleInput').init(
                    placeholder='title'
                ), Layout.Top,
                TextInput(self, 'DescriptionInput').init(
                    placeholder='description (optional)'
                ), Layout.Top,
                Label(self, 'HintLbl1', False).init(
                    wrap=True, alignment=Layout.Center,
                    text='Hint: Create category like "Social Media" to store your Twitter, Facebook or Instagram personal data'
                ),
                Spacer(False, True),
                ErrorLabel(self, 'ErrorLbl').init(
                    wrap=True, alignment=Layout.Center
                ), Layout.Center,
                Button(self, 'CreateBtn').init(
                    text='Create', slot=self.execute_create
                ),
                Frame(self, 'SaveCancelFrame', False).init(
                    layout=Layout.horizontal().init(
                        spacing=20,
                        items=[
                            Button(self, 'SaveBtn').init(
                                text='Save', slot=self.execute_save
                            ),
                            Button(self, 'CancelBtn').init(
                                text='Cancel', slot=self.execute_cancel
                            )
                        ]
                    )
                ),
                Layout.horizontal().init(
                    items=[
                        Button(self, 'ImportBtn', False).init(
                            text='Import item', icon=ICONS.IMPORT, slot=self.import_item
                        ),
                        Button(self, 'AddItemBtn', False).init(
                            text='Add item', icon=ICONS.PLUS, slot=self.add_item
                        )
                    ]
                )
            ]
        ))
        return self

    @pyqtSlot()
    def toggle_favourite(self):
        if not API.category:
            return True
        updated_category = API.set_category_favourite(API.category['id'], self.FavouriteButton.is_favourite)
        if category_id := updated_category.get('id'):
            self.ErrorLbl.setText('')
            CONTEXT.LeftMenu.refresh_categories()
            return True
        self.ErrorLbl.setText('Internal error, please try again')
        return False

    @pyqtSlot()
    def add_item(self):
        CONTEXT.RightPages.setCurrentWidget(CONTEXT.RightPagesItem)
        CONTEXT.RightPagesItem.show_create()

    def show_create(self):
        API.category = None
        self.HintLbl1.setVisible(True)
        self.CreateBtn.setVisible(True)
        self.EditBtn.setVisible(False)
        self.SaveCancelFrame.setVisible(False)
        self.AddItemBtn.setVisible(False)
        self.ImageButton.setIcon(ICONS.CATEGORY.icon)
        self.ImageButton.setDisabled(False)
        self.ImageButton.image_bytes = None
        self.FavouriteButton.unset_favourite()
        self.TitleInput.setEnabled(True)
        self.TitleInput.setText('')
        self.DescriptionInput.setDisabled(False)
        self.DescriptionInput.setText('')
        self.DescriptionInput.setVisible(True)
        self.ImportBtn.setVisible(False)

        CONTEXT.CentralItems.refresh_items([])
        CONTEXT.RightPages.setCurrentWidget(CONTEXT.RightPagesCategory)
        CONTEXT.RightPages.expand()

    @pyqtSlot()
    def import_item(self):
        filepath, _ = QFileDialog.getOpenFileName(self, 'Choose a file to import', '', 'JSON Files (*.json)')
        if filepath:
            imported_item = API.import_item(filepath)
            if item_id := imported_item.get('id'):
                CONTEXT.LeftMenu.refresh_categories()
                CONTEXT.CentralItems.refresh_items()
                CONTEXT.RightPagesItem.show_item(imported_item)

    @pyqtSlot()
    def execute_delete(self):
        if API.delete_category(API.category['id']).get('id'):
            self.TitleInput.setText('')
            self.DescriptionInput.setText('')
            self.DeleteBtn.setVisible(False)

            CONTEXT.LeftMenu.refresh_categories()
            self.show_create()
        else:
            self.ErrorLbl.setText('Internal error, please try again')

    @pyqtSlot()
    def execute_edit(self):
        self.ImportBtn.setVisible(False)
        self.CreateBtn.setVisible(False)
        self.SaveCancelFrame.setVisible(True)
        self.AddItemBtn.setVisible(False)
        self.ImageButton.setDisabled(False)
        self.EditBtn.setVisible(False)
        self.TitleInput.setEnabled(True)
        self.DescriptionInput.setDisabled(False)
        self.DescriptionInput.setVisible(True)
        self.DeleteBtn.setVisible(True)

    @pyqtSlot()
    def execute_save(self):
        if not len(title := self.TitleInput.text()):
            return self.ErrorLbl.setText('Title can not be empty')
        prev_icon = API.category['icon']
        updated_category = API.update_category(API.category['id'], {
            'icon': self.ImageButton.image_bytes_str, 'title': title,
            'description': self.DescriptionInput.toPlainText(), 'is_favourite': self.FavouriteButton.is_favourite
        })
        if category_id := updated_category.get('id'):
            CONTEXT.LeftMenu.refresh_categories()
            self.execute_cancel()
            self.show_category(API.category)

            if prev_icon != (curr_icon := API.category['icon']):
                utils.save_icon(curr_icon)
        else:
            self.ErrorLbl.setText('Internal error, please try again')

    @pyqtSlot()
    def execute_cancel(self):
        self.ErrorLbl.setText('')
        self.TitleInput.setEnabled(False)
        self.ImageButton.setIcon(Icon(API.category['icon']).icon)
        self.ImageButton.setDisabled(True)
        self.DescriptionInput.setDisabled(True)
        self.DescriptionInput.setVisible(API.category['description'] is not None)
        self.SaveCancelFrame.setVisible(False)
        self.AddItemBtn.setVisible(True)
        self.DeleteBtn.setVisible(False)
        self.EditBtn.setVisible(True)

    def show_category(self, category: dict[str, Any]):
        API.category = category
        self.FavouriteButton.set(API.category['is_favourite'])
        self.TitleInput.setEnabled(False)
        self.TitleInput.setText(API.category['title'])
        self.ImageButton.setIcon(Icon(API.category['icon']).icon)
        self.ImageButton.setDisabled(True)
        self.DescriptionInput.setText(API.category['description'])
        self.DescriptionInput.setDisabled(True)
        self.DescriptionInput.setVisible(API.category['description'] is not None)
        self.ErrorLbl.setText('')
        self.SaveCancelFrame.setVisible(False)
        self.AddItemBtn.setVisible(True)
        self.CreateBtn.setVisible(False)
        self.EditBtn.setVisible(True)
        self.DeleteBtn.setVisible(False)
        self.HintLbl1.setVisible(False)
        self.ImportBtn.setVisible(True)

        CONTEXT.RightPages.setCurrentWidget(CONTEXT.RightPagesCategory)
        CONTEXT.RightPages.expand()
        CONTEXT.CentralItems.refresh_items()

    @pyqtSlot()
    def execute_create(self):
        title = self.TitleInput.text()
        if not len(title):
            return self.ErrorLbl.setText('Title can not be empty')
        created_category = API.create_category({
            'icon': self.ImageButton.image_bytes_str, 'title': title,
            'description': self.DescriptionInput.toPlainText(), 'is_favourite': self.FavouriteButton.is_favourite
        })
        if created_category.get('id'):
            CONTEXT.LeftMenu.refresh_categories()
            self.show_category(API.category)
        else:
            self.ErrorLbl.setText('Internal error, please try again')
