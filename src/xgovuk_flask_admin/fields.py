# Create a custom field that handles the list <-> string conversion
from wtforms import TextAreaField


class ArrayTextAreaField(TextAreaField):
    def _value(self):
        """Convert list to newline-separated string for display."""
        if self.data:
            if isinstance(self.data, list):
                # Filter out empty strings and join with newlines
                return "\n".join(str(item) for item in self.data if item)
            return str(self.data)
        return ""

    def process_formdata(self, valuelist):
        """Convert newline-separated string to list."""
        if valuelist:
            # Split by newlines, strip whitespace, filter out empty lines
            self.data = [
                line.strip() for line in valuelist[0].split("\n") if line.strip()
            ]
        else:
            self.data = []
