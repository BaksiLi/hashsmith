"""A wrapper for executing hashcat commands and monitoring their status."""
import subprocess
from pathlib import Path
from typing import List

class HashcatRunner:
    def __init__(self, hashcat_path: str):
        self.hashcat_path = hashcat_path

    def run(self, command: List[str]) -> bool:
        """Runs a hashcat command and checks for cracked status."""
        print(f"\n🔥 Running command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=False)

        if "Cracked" in result.stdout or "Cracked" in result.stderr:
            print("\n🎉 CRACKED! Password found.")
            try:
                session_arg_index = command.index("--session") + 1
                session_name = command[session_arg_index]
                
                # Find the hash file in the command to show results
                hash_file = ""
                for arg in command:
                    # A simple heuristic to find the hash file path
                    if Path(arg).is_file() and 'hash' in Path(arg).name:
                        hash_file = arg
                        break
                
                if not hash_file: raise ValueError("Hash file not found in command")
                
                self._show_cracked_password(hash_file, session_name, command)
            except (ValueError, IndexError) as e:
                print(f"   Could not automatically show cracked password. Please check the potfile. Error: {e}")
            return True
        
        print("   ... not found in this phase.")
        return False

    def _show_cracked_password(self, hash_file: str, session_name: str, original_command: List[str]):
        """Display the cracked password from hashcat output."""
        show_cmd = [self.hashcat_path, "--show", hash_file, "--session", session_name]
        if "--hex-salt" in original_command:
            show_cmd.append("--hex-salt")
        cracked_output = subprocess.run(show_cmd, capture_output=True, text=True, check=False)
        print(f"--- Cracked Password ---\n{cracked_output.stdout.strip()}\n----------------------") 