"""
    SALESFORCE API MODULE
"""
from simple_salesforce import Salesforce, SFType
from main_app.Constants.sf_config import ConnectionString

def get_access_token_by_refresh_token():
    """
    :return:
    """
    data = {'client_secret': ConnectionString.CLIENT_SECRET,
            'client_id': ConnectionString.CONSUMER_KEY,
            'redirect_uri': ConnectionString.REDIRECT_URI,
            'refresh_token': ConnectionString.REFRESH_TOKEN}
    import requests
    response = requests.post("https://test.salesforce.com/services/oauth2/token?grant_type=refresh_token", data=data)
    print(response.json())
    return response.json().get("access_token")


def get_refresh_token():
    data = {'client_secret': ConnectionString.CLIENT_SECRET,
            'client_id': ConnectionString.CONSUMER_KEY,
            'redirect_uri': ConnectionString.REDIRECT_URI,
            }
    import requests
    response = requests.post("https://test.salesforce.com/services/oauth2/authorize?grant_type=authorization&response_type=token", data=data)
    print(response.json())
    return response.json().get("refresh_token")


class SFConnectAPI:
    """
        SALESFORCE API CLASS
    """
    sf = None
    sf_bulk = None

    def __init__(self, sf_config=ConnectionString):
        """
        :param sf_config:
        """
        print("connecting with salesforce.")
        self.security_token = get_access_token_by_refresh_token()
        self.sf = Salesforce(instance=sf_config.SF_URL,
                             session_id=self.security_token,
                             # security_token=sf_config.SECURITY_TOKEN,
                             sandbox=True)
        print("connection success")

    def get_header(self, session_id):
        """
        :return:
        """
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + session_id,
            'X-PrettyPrint': '1'
        }

    def get_access_token(self):
        """
        :return:
        """
        data = {'client_secret': ConnectionString.CLIENT_SECRET,
                'username': ConnectionString.USERNAME,
                'password': ConnectionString.PASSWORD+ConnectionString.SECURITY_TOKEN,
                'client_id': ConnectionString.CONSUMER_KEY,
                'redirect_uri': ConnectionString.REDIRECT_URI}
        import requests
        response = requests.post("https://test.salesforce.com/services/oauth2/token?grant_type=password", data=data)
        print(response.json())
        return response.json().get("access_token")

    def execute_soql(self, query):
        """
        :param sf_conn:
        :param query:
        :param host:
        :return:
        """
        result = self.sf.query(query)
        return result

    def create_record(self, object_name=None, data=None):
        session_id = self.security_token
        try:
            sf_obj = SFType(object_name, session_id, ConnectionString.SF_URL)
            result = sf_obj.create(data)
            print(repr(result))
        except Exception as ex:
            result = ex
            print(repr(ex))
        return result

    def update_record(self, record_id=None, object_name=None, data=None):
        session_id = self.security_token
        try:
            sf_obj = SFType( object_name, session_id, ConnectionString.SF_URL )
            result = sf_obj.update(record_id, data)
        except Exception as ex:
            result = ex
            print(repr(ex))
        return result

    def get_sf_fields(self, url, sfobj_api=None, dummy=False):
        """
        :param url:
        :param sfobj_api:
        :param dummy:
        :return sf_object_fields:
        """
        import json
        if sfobj_api:
            sftype_object = SFType(sfobj_api,
                                   session_id=self.security_token,
                                   sf_instance=url)
            describe = sftype_object.describe(headers=None)
            sf_object_fields = describe['fields']
            return sf_object_fields
        return None

    def get_position_values(self):
        fields = self.get_sf_fields(url=ConnectionString.SF_URL, sfobj_api='Resume_Google_Drive_Link__c', )
        values = [value['label'] for value in fields[17]['picklistValues']]
        print(values)
        return values

