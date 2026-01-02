"""
Tree widget for displaying vault structure.
"""

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from ..vault import VaultIndex, IndexNode


class VaultTreeWidget(QTreeWidget):
    """Tree widget for displaying encrypted vault structure."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setHeaderLabel("Vault Contents")
        self.setAlternatingRowColors(True)

        self.index: VaultIndex | None = None
        self.node_items: dict[str, QTreeWidgetItem] = {}

    def load_index(self, index: VaultIndex):
        """
        Load and display a vault index.

        Args:
            index: Vault index to display
        """
        self.clear()
        self.index = index
        self.node_items.clear()

        # Build tree from root nodes (nodes with no parent)
        root_nodes = [node for node in index.nodes.values() if node.parent_id is None]

        for node in root_nodes:
            self._add_node_recursive(node)

        self.expandAll()

    def _add_node_recursive(self, node: IndexNode, parent_item: QTreeWidgetItem | None = None):
        """
        Recursively add a node and its children to the tree.

        Args:
            node: Node to add
            parent_item: Parent tree item (None for root)
        """
        # Create tree item
        if parent_item is None:
            item = QTreeWidgetItem(self)
        else:
            item = QTreeWidgetItem(parent_item)

        # Set node name
        item.setText(0, node.name)

        # Set icon based on type
        if node.node_type == "folder":
            item.setText(0, f"📁 {node.name}")
        else:
            item.setText(0, f"📄 {node.name}")

        # Store node ID in item data
        item.setData(0, Qt.ItemDataRole.UserRole, node.node_id)

        # Store item reference
        self.node_items[node.node_id] = item

        # Add children
        if self.index:
            children = self.index.get_children(node.node_id)
            for child in sorted(children, key=lambda n: (n.node_type, n.name)):
                self._add_node_recursive(child, item)

    def get_selected_node_id(self) -> str | None:
        """
        Get the node ID of the currently selected item.

        Returns:
            str | None: Node ID or None if nothing selected
        """
        selected_items = self.selectedItems()
        if not selected_items:
            return None

        item = selected_items[0]
        return item.data(0, Qt.ItemDataRole.UserRole)

    def get_selected_node(self) -> IndexNode | None:
        """
        Get the currently selected node.

        Returns:
            IndexNode | None: Selected node or None
        """
        node_id = self.get_selected_node_id()
        if node_id is None or self.index is None:
            return None

        return self.index.get_node(node_id)
