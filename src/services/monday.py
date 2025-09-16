from src.config import settings

class MondayService():
    def __init__(self):
        self.api_token = settings.monday_api_token
        self.api_endpoint = settings.monday_api_endpoint

    def get_boards(self):
        # Implementation to interact with Monday.com API to get boards
        pass

    def create_item(self, board_id: int, item_name: str):
        # Implementation to create an item on a specific board
        pass
