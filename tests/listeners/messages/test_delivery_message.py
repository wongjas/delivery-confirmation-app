import logging
from unittest.mock import Mock

from slack_bolt import BoltContext, Say

from listeners.messages.delivery_message import delivery_message_callback


test_logger = logging.getLogger(__name__)


class TestDeliveryMessage:
    def setup_method(self):
        self.fake_say = Mock(Say)
        self.fake_context = BoltContext(matches=["DEL-12345"])

    def test_delivery_message_callback_success(self):
        delivery_message_callback(
            context=self.fake_context,
            say=self.fake_say,
            logger=test_logger,
        )

        # Verify say was called once
        self.fake_say.assert_called_once()

        # Get the blocks that were passed to say
        call_args = self.fake_say.call_args
        blocks = call_args.kwargs.get("blocks")

        # Verify the structure of the blocks
        assert blocks is not None
        assert len(blocks) == 2

        # Check section block
        section_block = blocks[0]
        assert section_block["type"] == "section"
        assert "DEL-12345" in section_block["text"]["text"]
        assert "submitted" in section_block["text"]["text"]

        # Check actions block
        actions_block = blocks[1]
        assert actions_block["type"] == "actions"
        assert len(actions_block["elements"]) == 2

        # Check approve button
        approve_button = actions_block["elements"][0]
        assert approve_button["action_id"] == "approve_delivery"

        # Check deny button
        deny_button = actions_block["elements"][1]
        assert deny_button["action_id"] == "deny_delivery"

    def test_delivery_message_callback_different_delivery_id(self):
        # Test with a different delivery ID
        self.fake_context = BoltContext(matches=["DEL-67890"])

        delivery_message_callback(
            context=self.fake_context,
            say=self.fake_say,
            logger=test_logger,
        )

        self.fake_say.assert_called_once()

        # Get the blocks and verify the delivery ID is used correctly
        call_args = self.fake_say.call_args
        blocks = call_args.kwargs.get("blocks")

        section_block = blocks[0]
        assert "DEL-67890" in section_block["text"]["text"]

    def test_delivery_message_callback_context_access_exception(self, caplog):
        # Test when context access throws an exception (e.g., missing matches)
        self.fake_context = BoltContext()  # No matches

        delivery_message_callback(
            context=self.fake_context,
            say=self.fake_say,
            logger=test_logger,
        )

        # Verify the exception was logged
        assert len(caplog.records) > 0
        # The error should be logged since accessing matches[0] will fail
