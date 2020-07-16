class HeaderLinkState:
    """helper to assign active class to current page in header"""

    def __init__(self, page):
        self.page = page
        self.review = ""
        self.cards = ""
        self.stats = ""
        self.settings = ""
        self.set_corresponding_page_to_active()

    def set_corresponding_page_to_active(self):
        if self.page:
            setattr(self, self.page, "active")
