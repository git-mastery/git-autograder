import re


class RoleMarker: 
    """Utility class for handling role markers in text."""
    
    PATTERN = re.compile(r"^\[ROLE:([a-zA-Z0-9_-]+)\]\s*", re.IGNORECASE)

    @staticmethod
    def has_role_marker(text: str) -> bool:
        """Check if text contains a role marker."""
        return RoleMarker.PATTERN.match(text) is not None