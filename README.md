# WiseDinosaur

WiseDinosaur is an interactive robotic assistant that combines the fascination of dinosaurs with modern technology. It uses advanced computer vision and speech recognition to interact with users, responding to voice commands and following them around the room. This project aims to create an engaging educational tool that brings the ancient world to life, allowing users to learn about dinosaurs in an interactive and fun way.

## Technologies Used

- **Computer Vision**: OpenCV and cvzone for pose detection and tracking.
- **Speech Recognition**: Utilizes Python's `speech_recognition` library for understanding user commands.
- **Text-to-Speech**: Leverages `gTTS` for generating speech from text, allowing the dinosaur to "speak."
- **Audio Processing**: `pydub` for handling audio effects like dinosaur roars.
- **Multiprocessing**: For managing concurrent execution of vision tracking and speech interaction.
- **OpenAI's GPT-3**: Powers dynamic and intelligent conversations with users.
- **Pygame**: Used for additional audio handling and possibly game mechanics.

## Installation

Before running WiseDinosaur, you need to install its dependencies. Ensure you have Python 3.6 or newer installed on your system.

1. Clone the repository:
git clone https://github.com/YourUsername/WiseDinosaur.git

2. Navigate to the project directory:
cd WiseDinosaur

3. Install the required Python packages:
```
pip install -r requirements.txt
```

## Running the Code

To start interacting with WiseDinosaur, follow these steps:

1. Ensure you have a microphone and webcam connected to your computer.
2. Run the main script:
```
python Detector.py
```

3. Interact with WiseDinosaur using voice commands. Say "goodbye" to stop the interaction.

## How It Works

- **Vision Tracking**: The program uses your webcam to detect your position and movements, allowing the robotic dinosaur to follow you around.
- **Voice Interaction**: Speak to WiseDinosaur, and it will respond with voice-generated answers. It can answer questions, tell you about dinosaurs, or just chat.
- **Learning and Fun**: Besides interaction, WiseDinosaur aims to educate users about dinosaurs, their habits, and their world in an engaging manner.

## Notes
- **MP3**: The MP3 directory is meant to store any MP3 files that the robot will use to produce a specified noise.
- **GPT-3**: The GPT-3 directory is meant to store any files that are used to train the GPT-3 model.
- **JSON**: The Json files are meant to store any data that is used to train the GPT-3 model.

## Challenges Faced

- Integrating speech recognition and response generation in real-time with robotic movements.
- Ensuring accurate pose detection and smooth following mechanism for the robot.
- Crafting engaging and informative conversational responses using GPT-3.

## Contributing

Contributions to WiseDinosaur are welcome! Whether it's bug fixes, new features, or improvements to the documentation, feel free to fork the repository and submit a pull request.



