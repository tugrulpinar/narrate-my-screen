import base64
import os
import time

from dotenv import load_dotenv
from elevenlabs import generate, play, set_api_key, Voice, VoiceSettings
from openai import OpenAI
from PIL import ImageGrab
import pygame

SCREENSHOTS_FOLDER_NAME = "screenshots"
AUDIO_FILES_FOLDER_NAME = "audio"
BOUNDING_BOX = (0, 30, 1920, 1030)

NARRATOR = "Sir David Attenborough"
DOCUMENTARY_TYPE = "Nature"

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
set_api_key(os.environ.get("ELEVENLABS_API_KEY"))
pygame.init()


def take_screenshot(order_number: int) -> str:
    image_path = os.path.join(
        os.getcwd(), SCREENSHOTS_FOLDER_NAME, f"{order_number}_screenshot.jpg"
    )
    ss_img = ImageGrab.grab(bbox=BOUNDING_BOX)
    ss_img.save(image_path)

    return image_path


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def generate_new_line(base64_image: str) -> list[dict]:
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Describe this image.",
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        },
    ]


def analyze_image(base64_image: str, script: list[dict]) -> str:
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": f"You are {NARRATOR}. Narrate the screenshots from a software developer as if it is a {DOCUMENTARY_TYPE} documentary. "
                "Make it snarky and funny. Don't repeat yourself. Make it short. If I do anything remotely interesting, make a big deal about it! "
                "Limit your output to maximum two sentences.",
            },
        ]
        + script
        + generate_new_line(base64_image),
        max_tokens=500,
    )
    response_text = response.choices[0].message.content
    return response_text


def play_audio(text: str) -> None:
    audio = generate(
        text=text,
        voice=Voice(
            voice_id="fTa66eq1WTYWiITP51ZV",
            settings=VoiceSettings(
                stability=0.6, similarity_boost=0.2, style=0.8, use_speaker_boost=True
            ),
        ),
    )

    play(audio)


# def generate_audio(text: str, order_number: int) -> str:
#     audio_file_path = os.path.join(
#         os.getcwd(), AUDIO_FILES_FOLDER_NAME, f"{order_number}_audio.mp3"
#     )
#     response = client.audio.speech.create(model="tts-1", voice="fable", input=text)

#     response.stream_to_file(audio_file_path)

#     return audio_file_path


# def play_audio(audio_file_path: str) -> None:
#     my_sound = pygame.mixer.Sound(audio_file_path)
#     my_sound.play()
#     # prevent the audio overlaps
#     time.sleep((my_sound.get_length() // 2) + 1.5)


def main() -> None:
    script = []
    counter = 0

    while True:
        # take screenshot
        print("Taking a screenshot! 📷")
        image_path = take_screenshot(order_number=counter)

        # getting the base64 encoding
        base64_image = encode_image(image_path)

        print(f"👀 {NARRATOR} is watching...")
        analysis = analyze_image(base64_image, script=script)

        print(f"🎙️ {NARRATOR} says:")
        print(analysis)

        # audio_file_path = generate_audio(analysis, order_number=counter)

        # play_audio(audio_file_path=audio_file_path)

        play_audio(analysis)

        script = script + [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe this image (user uploaded image)",
                    },
                ],
            },
            {"role": "assistant", "content": analysis},
        ]

        counter += 1


if __name__ == "__main__":
    main()
