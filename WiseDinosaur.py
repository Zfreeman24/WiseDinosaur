import random
import speech_recognition as sr
import openai
import os
import pygame
import json
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play


API_KEY = "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"

def load_json_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def listen_to_speech(timeout=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise, please wait...")
        r.adjust_for_ambient_noise(source)
        print("You can speak now.")
        audio = r.listen(source, timeout=timeout)
        try:
            speech_as_text = r.recognize_google(audio)
            print("Transcribed speech:", speech_as_text)
            return speech_as_text
        except sr.UnknownValueError:
            print("Could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

def speak_text(text):
    # Randomly select an accent's tld
    accents = load_json_data("json/accents.json")
    tld = random.choice(list(accents.values()))
    
    # Ensure the directory exists
    mp3_directory = "mp3"
    os.makedirs(mp3_directory, exist_ok=True)
    mp3_path = os.path.join(mp3_directory, "response.mp3")

    # Generate speech with the selected accent
    tts = gTTS(text=text, lang='en', tld = tld, slow=False)
    tts.save(mp3_path)
    
    # Play the generated speech
    sound = AudioSegment.from_mp3("./mp3/response.mp3")
    play(sound)

def ask_openai(prompt, conversation_history):
    openai.api_key = API_KEY
    # Include a reminder of the dinosaur's perspective in every prompt
    prompt_reinforcement = "Remember, I'm a dinosaur with no understanding of modern concepts like technology or the stock market. I can only relate things to my prehistoric experiences."
    messages = conversation_history + [
        {"role": "system", "content": "The assistant is a dinosaur and should respond from that perspective, unaware of modern technologies or concepts."},
        {"role": "user", "content": prompt_reinforcement + " " + prompt}
    ]
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return_response = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": return_response})
    return return_response, conversation_history

def play_roar_sound_if_condition_met(distance):
    pygame.mixer.init()  # Initialize pygame mixer
    roar_sound = pygame.mixer.Sound("mp3/roar.mp3")  # Load the MP3 file

    # Check if the condition is met and play the sound if it is
    if distance > 5.0:
        roar_sound.play()
        pygame.time.wait(int(roar_sound.get_length() * 1000))  # Wait for the sound to finish playing

def get_dinosaur_prompt_and_personality(dinosaurs):
    dinosaur, personality = random.choice(list(dinosaurs.items()))
    template = f"This is a conversation with a {dinosaur}, who is {personality}."
    return template


def main():
    dinosaurs = load_json_data("json/personalities.json")

    conversation_history = []
    dinosaur_prompt = get_dinosaur_prompt_and_personality(dinosaurs)
    print(f"Context: {dinosaur_prompt}")
    conversation_history.append({"role": "system", "content": dinosaur_prompt})

    while True:
        user_speech = listen_to_speech()
        if user_speech is None or user_speech.lower() == "goodbye":
            speak_text("Goodbye! It was nice talking with you.")
            break  # Exit the loop if speech is not understood, an error occurs, or the user says "goodbye"

        # Generate a response from GPT
        gpt_response, conversation_history = ask_openai(user_speech, conversation_history)
        print(f"GPT-3 Response: {gpt_response}")

        # Speak out GPT's response
        speak_text(gpt_response)

    # Example usage of playing sound based on condition
    distance = 5.1  # Example condition; replace or modify as needed
    play_roar_sound_if_condition_met(distance)

if __name__ == "__main__":
    main()
