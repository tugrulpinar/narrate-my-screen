import base64
import os
import time

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from openai import OpenAI
from PIL import ImageGrab

SCREENSHOTS_FOLDER_NAME = "screenshots"
AUDIO_FILES_FOLDER_NAME = "audio"
BOUNDING_BOX = (0, 30, 1920, 1030)

NARRATOR = "Sir David Attenborough"
DOCUMENTARY_TYPE = "Nature"

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
elevenlabs_client = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))


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
    return [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What is in this image?",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }]


def analyze_image(base64_image: str, script: list[dict]) -> str:
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You are {NARRATOR}. Narrate the screenshots from a software developer as if it is a {DOCUMENTARY_TYPE} documentary. "
                "Make it snarky and funny. Don't repeat yourself. Make it short. "
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
    audio = elevenlabs_client.generate(text=text)
    play(audio)


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
