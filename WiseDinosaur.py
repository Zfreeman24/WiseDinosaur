import random
import speech_recognition as sr
import openai
import pygame
import json
from gtts import gTTS
from io import BytesIO
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
    """Convert text to speech and play it using the globally selected accent."""
    global tld  # Ensure we're using the global variable
    
    # Generate speech with gTTS using the selected accent for the entire conversation
    tts = gTTS(text=text, lang='en', tld=tld, slow=False)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)  # Reset the pointer of the BytesIO object to the beginning
    
    # Load the audio from the BytesIO object and play it
    sound = AudioSegment.from_file(mp3_fp, format="mp3")
    play(sound)


def ask_openai(prompt, conversation_history):
    openai.api_key = API_KEY
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
    pygame.mixer.init()
    roar_sound = pygame.mixer.Sound("mp3/roar.mp3")
    if distance > 5.0:
        roar_sound.play()
        pygame.time.wait(int(roar_sound.get_length() * 1000))

def get_dinosaur_prompt_and_personality(dinosaurs):
    dinosaur, personality = random.choice(list(dinosaurs.items()))
    return dinosaur, personality  # Return just the dinosaur and personality


def get_random_dinosaur_name():
    """Generate a random name for the dinosaur."""
    # Example names, feel free to expand this list
    names = ["Rex", "Spike", "Leaf", "Roary", "Jade"]
    return random.choice(names)

def main():
    dinosaurs = load_json_data("json/personalities.json")
    accents = load_json_data("json/accents.json")
    favorite_activities_list = load_json_data("favorite_activities.json")  # Load favorite activities from JSON

    
    global tld
    tld = random.choice(list(accents.values()))

    conversation_history = []
    dinosaur, personality = get_dinosaur_prompt_and_personality(dinosaurs)
    
    dinosaur_name = get_random_dinosaur_name()

    favorite_activities = random.choice(favorite_activities_list)

    
    # Adjust the greeting to properly format the dinosaur's type and personality
    initial_greeting = f"Hello! My name is {dinosaur_name}, and I am a {dinosaur}. I am {personality}. I love {favorite_activities}. What's on your mind today?"
    print(f"GPT-3 Response: {initial_greeting}")  # Display the greeting
    
    # Speak the initial greeting
    speak_text(initial_greeting)

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
    distance = 0;
    play_roar_sound_if_condition_met(distance)

if __name__ == "__main__":
    main()
