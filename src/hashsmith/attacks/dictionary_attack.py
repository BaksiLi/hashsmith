"""
Dictionary attack module for hashcat wordlist-based attacks.
"""

from pathlib import Path


class DictionaryAttack:
    """
    Handles dictionary-based attacks using wordlists.

    Can apply rules to wordlists and manage different attack strategies.
    """

    def __init__(self, hashcat_path: str = "hashcat"):
        self.hashcat_path = hashcat_path

    def generate_command(
        self,
        hash_file: Path,
        wordlist: Path,
        rule_file: Path | None = None,
        session_name: str = "dict_attack",
        extra_args: list[str] = None,
    ) -> list[str]:
        """Generate hashcat command for dictionary attack."""

        cmd = [
            self.hashcat_path,
            "-m",
            "1410",  # SHA256($pass.$salt)
            "-a",
            "0",  # Dictionary attack
            "--hex-salt",
            str(hash_file),
            str(wordlist),
        ]

        if rule_file and rule_file.exists():
            cmd.extend(["-r", str(rule_file)])

        if extra_args:
            cmd.extend(extra_args)

        cmd.extend(["--session", session_name])

        return cmd
