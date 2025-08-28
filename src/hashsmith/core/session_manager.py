"""Manages hashcat sessions (restore, cleanup, etc.)."""

from pathlib import Path


class SessionManager:
    def __init__(self, session_dir: Path = Path(".")):
        self.session_dir = session_dir

    def list_sessions(self) -> list:
        """List all available session restore files."""
        return list(self.session_dir.glob("*.restore"))

    def cleanup_session(self, session_name: str):
        """Remove restore and potfiles for a given session."""
        restore_file = self.session_dir / f"{session_name}.restore"
        potfile_bak = self.session_dir / f"{session_name}.potfile.bak"

        if restore_file.exists():
            restore_file.unlink()
            print(f"Removed restore file: {restore_file}")
        if potfile_bak.exists():
            potfile_bak.unlink()
            print(f"Removed potfile backup: {potfile_bak}")
