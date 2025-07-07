import logging
from unittest.mock import Mock, patch

from listeners.actions.approve_deny_buttons import (
    approve_delivery_callback,
    deny_delivery_callback,
)


test_logger = logging.getLogger(__name__)


class TestApproveDeliveryCallback:
    def setup_method(self):
        self.fake_ack = Mock()
        self.fake_client = Mock()
        self.fake_body = {
            "message": {"text": "New delivery *DEL-12345* has arrived"},
            "container": {
                "channel_id": "C1234567890",
                "message_ts": "1234567890.123456",
            },
            "trigger_id": "156772938.1827394",
            "user": {"id": "U1234567890"},
        }

    def test_approve_delivery_callback_success(self):
        """Test successful approval flow"""
        approve_delivery_callback(
            ack=self.fake_ack,
            body=self.fake_body,
            client=self.fake_client,
            logger=test_logger,
        )

        # Verify ack was called
        self.fake_ack.assert_called_once()

        # Verify chat_update was called with correct parameters
        self.fake_client.chat_update.assert_called_once()
        chat_update_args = self.fake_client.chat_update.call_args.kwargs
        assert chat_update_args["channel"] == "C1234567890"
        assert chat_update_args["ts"] == "1234567890.123456"
        assert len(chat_update_args["blocks"]) == 1
        assert "DEL-12345" in chat_update_args["blocks"][0]["text"]["text"]

        # Verify views_open was called with correct parameters
        self.fake_client.views_open.assert_called_once()
        views_open_args = self.fake_client.views_open.call_args.kwargs
        assert views_open_args["trigger_id"] == "156772938.1827394"

        # Check modal structure
        view = views_open_args["view"]
        assert view["type"] == "modal"
        assert view["callback_id"] == "approve_delivery_view"
        assert view["title"]["text"] == "Approve Delivery"
        assert view["private_metadata"] == "DEL-12345"
        assert len(view["blocks"]) == 4

        # Check blocks structure
        blocks = view["blocks"]
        assert blocks[0]["type"] == "section"
        assert "DEL-12345" in blocks[0]["text"]["text"]

        # Check notes input block
        assert blocks[1]["type"] == "input"
        assert blocks[1]["block_id"] == "notes"
        assert blocks[1]["optional"] is True

        # Check location input block
        assert blocks[2]["type"] == "input"
        assert blocks[2]["block_id"] == "location"
        assert blocks[2]["optional"] is True

        # Check channel select block
        assert blocks[3]["type"] == "input"
        assert blocks[3]["block_id"] == "channel"
        assert blocks[3]["element"]["type"] == "channels_select"
        assert blocks[3]["element"]["initial_channel"] == "C1234567890"
        assert blocks[3]["optional"] is False

    def test_approve_delivery_callback_different_delivery_id(self):
        """Test with a different delivery ID"""
        self.fake_body["message"]["text"] = "New delivery *DEL-67890* arrived"

        approve_delivery_callback(
            ack=self.fake_ack,
            body=self.fake_body,
            client=self.fake_client,
            logger=test_logger,
        )

        # Verify the delivery ID is extracted correctly
        chat_update_args = self.fake_client.chat_update.call_args.kwargs
        assert "DEL-67890" in chat_update_args["blocks"][0]["text"]["text"]

        views_open_args = self.fake_client.views_open.call_args.kwargs
        assert views_open_args["view"]["private_metadata"] == "DEL-67890"


class TestDenyDeliveryCallback:
    def setup_method(self):
        self.fake_ack = Mock()
        self.fake_client = Mock()
        self.fake_body = {
            "message": {"text": "New delivery *DEL-12345* has arrived"},
            "container": {
                "channel_id": "C1234567890",
                "message_ts": "1234567890.123456",
            },
            "user": {"id": "U1234567890"},
        }

    def test_deny_delivery_callback_success(self):
        """Test successful denial flow"""
        deny_delivery_callback(
            ack=self.fake_ack,
            body=self.fake_body,
            client=self.fake_client,
            logger=test_logger,
        )

        # Verify ack was called
        self.fake_ack.assert_called_once()

        # Verify chat_update was called with correct parameters
        self.fake_client.chat_update.assert_called_once()
        chat_update_args = self.fake_client.chat_update.call_args.kwargs
        assert chat_update_args["channel"] == "C1234567890"
        assert chat_update_args["ts"] == "1234567890.123456"
        assert len(chat_update_args["blocks"]) == 1

        # Check the updated message content
        updated_text = chat_update_args["blocks"][0]["text"]["text"]
        assert "DEL-12345" in updated_text

    def test_deny_delivery_callback_different_delivery_id(self):
        """Test with a different delivery ID"""
        self.fake_body["message"]["text"] = "New delivery *DEL-67890* has arrived"

        deny_delivery_callback(
            ack=self.fake_ack,
            body=self.fake_body,
            client=self.fake_client,
            logger=test_logger,
        )

        # Verify the delivery ID is extracted correctly
        chat_update_args = self.fake_client.chat_update.call_args.kwargs
        updated_text = chat_update_args["blocks"][0]["text"]["text"]
        assert "DEL-67890" in updated_text
