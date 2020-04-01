from unittest import TestCase
from unittest.mock import MagicMock

from evalytics.server.storages import Storage
from evalytics.server.communications_channels import CommunicationsChannel
from evalytics.server.core import DataRepository, CommunicationsProvider

class TestCore(TestCase):

    def test_data_repository(self):
        mock_storage = MagicMock(autospec=Storage)

        data_repository = DataRepository(storage=mock_storage)
        data_repository.get_employee_list()

        mock_storage.get_employee_list.assert_called_once()

    def test_communications_provider(self):
        destiny = "email"
        data = "this is ypur email"
        mock_comm_channel = MagicMock(autospec=CommunicationsChannel)

        comms_provider = CommunicationsProvider(
            communication_channel=mock_comm_channel)
        comms_provider.send(destiny, data)

        mock_comm_channel.send.assert_called_once()
    