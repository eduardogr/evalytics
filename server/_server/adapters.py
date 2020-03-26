
from .models import OrgChart

class FakeAdapter():
   
    def get_org_chart():
        return OrgChart()


class GoogleSheetsAdapter():
    
    def get_org_chart():
        # TODO: This adapter talks with google sheets api and returns an OrgChart model
        return OrgChart()