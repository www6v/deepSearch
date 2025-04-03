import random
import string
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

class Workspace:
    def __init__(self):
        self.state = {"status": "IN_PROGRESS", "blocks": {}, "answer": None}

    def to_string(self):
        """
        Converts the workspace state to a formatted string representation.

        Returns:
            str: A string representation of the workspace state
        """
        result = f"Status: {self.state['status']}\n"
        result += "Memory: \n"

        if not self.state["blocks"]:
            result += "... no memory blocks ...\n"
        else:
            for block_id, content in self.state["blocks"].items():
                result += f"<{block_id}>{content}</{block_id}>\n"

        return result

    def _generate_unique_block_id(self):
        """
        Generate a unique block ID in the format abc-123.

        Returns:
            str: A unique ID consisting of 3 lowercase letters, a hyphen, and 3 digits
        """
        while True:
            # Generate random ID in abc-123 format
            letters = "".join(random.choices(string.ascii_lowercase, k=3))
            digits = "".join(random.choices(string.digits, k=3))
            new_id = f"{letters}-{digits}"

            # Return ID if it's unique
            if new_id not in self.state["blocks"]:
                return new_id

    def update_blocks(
        self, status: str, blocks: List[Dict], answer: Optional[str] = None
    ):
        """
        Updates the workspace state with new status, blocks, and answer.

        Args:
            status (str): New status ("IN_PROGRESS" or "DONE")
            blocks (List[Dict]): List of block operations to apply
                Each dict should have:
                - "operation": "add" or "delete"
                - "content": content to add (for "add" operation)
                - "id": block id to delete (for "delete" operation)
            answer (Optional[str]): Final answer when status is "DONE"
        """
        # Update status
        self.state["status"] = status

        # Update blocks based on operations
        for block_op in blocks:
            operation = block_op.get("operation")

            if operation == "add":
                # Generate a unique block ID using helper function
                new_id = self._generate_unique_block_id()
                self.state["blocks"][new_id] = block_op.get("content", "")

            elif operation == "delete":
                block_id = block_op.get("id")
                if block_id in self.state["blocks"]:
                    del self.state["blocks"][block_id]

        # Update answer if provided
        if answer is not None:
            self.state["answer"] = answer

    def is_done(self):
        return self.state["status"] != "IN_PROGRESS"
