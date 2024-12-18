import speech_recognition as sr
import pyautogui
import threading
import queue

class VoiceNavigator:
    def __init__(self):
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Create a queue to manage voice commands
        self.command_queue = queue.Queue()
        
        # Flag to control the listening thread
        self.is_listening = True
        
        # Define command mappings
        self.commands = {
            'next': 'right',
            'previous': 'left',
            'slideshow': 'ctrl+f5',
            'exit': 'esc'
        }

    def listen_for_commands(self):
        """
        Continuously listen for voice commands using microphone input
        """
        with sr.Microphone() as source:
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Voice Navigator is ready!")
            print("Available commands:")
            print("- Say 'next' for right arrow")
            print("- Say 'previous' for left arrow")
            print("- Say 'slide show' for Ctrl+F5")
            print("- Say 'exit' to quit")
            
            while self.is_listening:
                try:
                    # Listen for audio input
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=3)
                    
                    # Process the audio in a separate thread to prevent blocking
                    threading.Thread(target=self.process_command, args=(audio,), daemon=True).start()
                
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"An error occurred: {e}")

    def process_command(self, audio):
        """
        Process the recognized speech and execute commands
        """
        try:
            # Use Google's speech recognition
            command = self.recognizer.recognize_google(audio).lower()
            print(f"Recognized: {command}")
            
            # Check for commands in the speech
            for voice_command, action in self.commands.items():
                if voice_command in command:
                    # Execute the corresponding action
                    if action == 'ctrl+f5':
                        # Special handling for Ctrl+F5
                        pyautogui.hotkey('ctrl', 'f5')
                        print("Ctrl+F5 pressed!")
                    elif action in ['right', 'left']:
                        # Simulate arrow key press
                        pyautogui.press(action)
                        print(f"{action.capitalize()} arrow key pressed!")
                    elif action == 'esc':
                        # Exit the application
                        pyautogui.press('esc')
                        print("Escape key pressed!")
                        self.is_listening = False
                    return
        
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

    def start(self):
        """
        Start the voice navigation system
        """
        # Start listening in a separate thread
        listener_thread = threading.Thread(target=self.listen_for_commands, daemon=True)
        listener_thread.start()

        # Keep main thread running
        try:
            while self.is_listening:
                # This prevents the main thread from exiting immediately
                threading.Event().wait(1)
        except KeyboardInterrupt:
            print("\nStopping Voice Navigator...")
            self.is_listening = False

def main():
    # Create and start the voice navigator
    navigator = VoiceNavigator()
    navigator.start()

if __name__ == "__main__":
    main()