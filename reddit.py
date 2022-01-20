import praw
from gtts import gTTS
from pydub import AudioSegment
import os
from PIL import Image, ImageDraw, ImageFont
from mutagen.mp3 import MP3
from sys import exc_info
import pygame.font as pf
import time

subreddit = 'AskReddit'
number_of_post = 1
post_skipped = 1
number_of_comments = 1
comments_skipped = 0
include_self_text = False

reddit_username = ''
reddit_password = ''

reddit = praw.Reddit(
                     )


def reddit_data(subreddit, number_of_post, post_skipped, number_of_comments, comments_skipped, include_self_text=False):
    main_return = [subreddit]
    post_num = 1
    for submission in reddit.subreddit(subreddit).hot(limit=number_of_post + post_skipped):
        if post_num <= post_skipped:
            post_num += 1
        else:
            if include_self_text == False:
                main_return.append(submission.title)
            if include_self_text == True:
                main_return.append(submission.title + "?%@" + submission.selftext)
            submission.comments.replace_more(limit=0)
            comments = submission.comments.list()[comments_skipped:number_of_comments + comments_skipped]
            comments_list = []
            for comment in comments:
                comments_list.append(comment.body)
            main_return.append(comments_list)
    return main_return


def text_to_speach(reddit_data):
    for i in range(len(reddit_data)):
        text = reddit_data[i]
        if i == 0:
            flnm = 'subreddit'
            tts = gTTS(text="r slash" + text, lang='en')
            tts.save('audio/' + flnm + ".mp3")
        else:
            if i % 2 == 1:
                flnm = 'post' + str((i + 1) / 2)
                tts = gTTS(text=text, lang='en')
                tts.save('audio/' + flnm + ".mp3")
            if i % 2 == 0:
                for k in range(len(text)):
                    ttsr = gTTS(text=text[k])
                    id = str(i / 2) + str(k + 1)
                    ttsr.save('audio/' + 'comment' + id + ".mp3")


def mp3combiner(export=False):
    from time import sleep
    sleep(2)
    full_audio = AudioSegment.from_mp3("audio/subreddit.mp3")
    for p in range(number_of_post):
        audio = AudioSegment.from_mp3("audio/post" + str(p + 1) + ".mp3")
        full_audio = full_audio + audio
        for c in range(number_of_comments):
            audio = AudioSegment.from_mp3("audio/comment" + str(p + 1) + str(c + 1) + ".mp3")
            full_audio = full_audio + audio

    if export == True:
        full_audio.export("audio/audio_full.mp3")

    return full_audio


def remove_mp3(remove_full_audio=False):
    os.remove("audio/subreddit.mp3")
    for p in range(number_of_post):
        os.remove("audio/post" + str(p + 1) + ".mp3")
        for c in range(number_of_comments):
            os.remove("audio/comment" + str(p + 1) + str(c + 1) + ".mp3")

    if remove_full_audio == True:
        os.remove("audio/audio_full.mp3")


def make_images(reddit_data, font_family, font_size):
    global Images_Made
    Images_Made = 0

    def ShortenList(l):
        newlist = []
        for sublist in l:
            if type(sublist) is list:
                for item in sublist:
                    newlist.append(item)
            else:
                newlist.append(sublist)
        newlist = [x for x in newlist if x != []]
        return newlist

    def GetFontSize(text, font, size, get_height=False):
        return pf.Font(font, size).size(text)[get_height]

    def Format(data):
        a, b = 0, len(data)
        new_data = []

        while True:
            wkdata = data[a:b]
            if GetFontSize(wkdata, family, size) < img_x - 2 * text_x:
                new_data.append(wkdata)
                if a >= b:
                    break
                a = b
                b = len(data) + 1
            b = b - 1
        return new_data

    pf.init()
    img_x, img_y = 1920, 1080
    text_x, text_y = 30, 30
    flat_reddit_data = ShortenList(reddit_data)
    family = font_family
    size = font_size

    for i in range(len(flat_reddit_data)):
        img = Image.new('RGB', (img_x, img_y), color=(25, 25, 25))
    drw = ImageDraw.Draw(img)
    font = ImageFont.truetype(family, size)

    data = (flat_reddit_data[i])
    new_data = Format(data)

    for r in range(len(new_data)):
        drw.text((text_x, text_y + r * GetFontSize(data, family, size, True)), new_data[r], font=font)

    img.save('images/' + str(i + 1) + ".png")
    Images_Made += 1


def remove_images():
    for i in range(Images_Made):
        os.remove("images/" + str(i + 1) + ".png")


def get_audio_length():
    audio_length = [MP3("audio/subreddit.mp3").info.length]
    for p in range(number_of_post):
        audio_length.append(MP3("audio/post" + str(p + 1) + ".mp3").info.length)
        for c in range(number_of_comments):
            audio_length.append(MP3("audio/comment" + str(p + 1) + str(c + 1) + ".mp3").info.length)
    return audio_length


def combine_image_audio():
    def combine(image, audio, output):
        os.system('ffmpeg -loglevel panic -loop 1 -framerate 15 -i ' + image + ' -i ' + audio +
               ' -c:v libx264 -crf 0 -preset veryfast -tune stillimage -c:a copy -shortest ' + output)

    for num in range(Images_Made):
        if (num - 1) % (number_of_post + number_of_comments) == 0:
            audio_file = 'post' + str((num - 1) / (number_of_post + number_of_comments) + 1)
        else:
            audio_file = 'comment' + str(((num - 1) / (number_of_post + number_of_comments) + 1)) + str(
                (num - 1) % (number_of_post + number_of_comments))


def remove_mp4():
    for i in range(Images_Made):
        os.remove('mp4/' + str(i + 1) + ".mp4")


def upload_Final():
    os.system("youtube-upload --title=\"Test0\" Final.mp4")
    os.remove("Final.mp4")


if __name__ == '__main__':
    start_time = time.time()
    try:
        reddit_data = reddit_data(subreddit, number_of_post, post_skipped, number_of_comments, comments_skipped,
                                  include_self_text)
        text_to_speach(reddit_data)
        mp3combiner(export=True)
        audio_length = get_audio_length()
        make_images(reddit_data, "OpenSans-Regular.ttf", 64)
        combine_image_audio()
        # combineMP4()
        remove_mp3()
        remove_images()
        remove_mp4()
        upload_Final()

    except Exception as e:
        print("Error: " + str(e))
        print("Line#: " + str(exc_info()[2].tb_lineno))
        raise

    except KeyboardInterrupt:
        print("Program Interrupted")

    finally:
        end_time = time.time()
        print("Time Elapsed: " + str(round(end_time - start_time, 1)) + " seconds")
