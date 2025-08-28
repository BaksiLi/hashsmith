"""A wrapper for executing Hashcat commands and monitoring their status.

This utility focuses on a friendly developer experience:
- Ensures the provided binary path is used consistently
- Prints the invoked command for reproducibility
- Attempts to display cracked credentials automatically when possible
"""

import subprocess
from pathlib import Path


class HashcatRunner:
    def __init__(self, hashcat_path: str):
        self.hashcat_path = hashcat_path

    def run(self, command: list[str]) -> bool:
        """Run a Hashcat command and report whether it cracked any hashes.

        Returns True if output indicates a cracked password, otherwise False.
        """
        # Ensure we invoke the configured binary, regardless of command[0]
        full_command = list(command)
        if not full_command:
            raise ValueError("Command cannot be empty")
        full_command[0] = self.hashcat_path

        print(f"\n🔥 Running command: {' '.join(full_command)}")
        result = subprocess.run(
            full_command, capture_output=True, text=True, check=False
        )

        # Hashcat commonly uses 0/1 for success/no-crack
        if result.returncode not in (0, 1):
            print("\n⚠️ Hashcat exited with a non-standard code:")
            print(result.stderr.strip())

        if "Cracked" in result.stdout or "Cracked" in result.stderr:
            print("\n🎉 CRACKED! Password found.")
            try:
                session_arg_index = full_command.index("--session") + 1
                session_name = full_command[session_arg_index]

                # Find the hash file in the command to show results
                hash_file = ""
                for arg in full_command:
                    # A simple heuristic to find the hash file path
                    if Path(arg).is_file() and "hash" in Path(arg).name:
                        hash_file = arg
                        break

                if not hash_file:
                    raise ValueError("Hash file not found in command")

                self._show_cracked_password(hash_file, session_name, full_command)
            except (ValueError, IndexError) as e:
                msg = (
                    "   Could not automatically show cracked password. "
                    "Please check the potfile. Error: "
                    f"{e}"
                )
                print(msg)
            return True

        print("   ... not found in this phase.")
        return False

    def _show_cracked_password(
        self, hash_file: str, session_name: str, original_command: list[str]
    ):
        """Display the cracked password from hashcat output."""
        show_cmd = [self.hashcat_path, "--show", hash_file, "--session", session_name]
        if "--hex-salt" in original_command:
            show_cmd.append("--hex-salt")
        cracked_output = subprocess.run(
            show_cmd, capture_output=True, text=True, check=False
        )
        print("--- Cracked Password ---")
        print(cracked_output.stdout.strip())
        print("----------------------")
