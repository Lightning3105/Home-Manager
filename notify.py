from gtts import gTTS
from playsound import playsound
import os


def say(*args):
	sentence = " ".join(args)
	filename = 'sound_output/' + sentence.replace(" ", "_") + ".mp3"
	if not os.path.exists('sound_output'):
		os.mkdir('sound_output')
	if os.path.exists(filename):
		playsound(filename)
	else:
		tts = gTTS(text=sentence, lang='en')
		tts.save(filename)
		playsound(filename)


if __name__ == "__main__":
	say("Hello there James")
