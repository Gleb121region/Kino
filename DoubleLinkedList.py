class Node:
    def __init__(self, data):
        self.item = data
        self.next = None
        self.prev = None


class DoublyLinkedList:
    def __init__(self):
        self.start_node = None
