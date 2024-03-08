'''
screen_recorder.py

This code defines a ScreenRecorder class in Python that facilitates screen recording on a system 
using ffmpeg. The class provides functionality to start and stop recording, split the recording 
into segments, remove duplicate frames, and concatenate the segments into a final video.
'''

import time
import subprocess
import os
import signal
from subprocess import PIPE
import logging


class ScreenRecorder:
    def __init__(self, dir, duration, split_num=2,
                 log_name: str = "screen_recorder"):
        self.dir = dir  # directory where the recording will be saved
        self.split_num = split_num  # number of segments to split the recording into
        self.split_duration = duration / self.split_num
        self.process = None
        self.logger = logging.getLogger(log_name)

    def remove_duplicated_file(self, file, unique_file_list):

        with open(file, 'r') as f:
            lines = f.readlines()

        new_lines = []
        for line in reversed(lines):
            if line not in new_lines:
                new_lines.insert(0, line)

        with open(unique_file_list, 'w') as f:
            f.writelines(new_lines)

    def start_recording(self):
        """
        Start the screen recording process using ffmpeg
        """

        cmd = ("ffmpeg -f x11grab -s $(xdpyinfo | grep 'dimensions:'|awk '{print $2}') -i :1"
               " -r 25 -vcodec libx264 -preset ultrafast -tune zerolatency "
               " -loglevel error"
               " -segment_time " + str(int(self.split_duration)) +
               " -f segment -segment_wrap " + str(int(self.split_num)) +
               " -segment_list " + os.path.join(self.dir, "out.ffconcat") +
               " -reset_timestamps 1 " +
               os.path.join(self.dir, "record_screen_%03d.mp4"))

        self.process = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE,
                                        shell=True, executable="/bin/bash",
                                        preexec_fn=os.setsid,  # to kill all related process
                                        encoding="utf-8")

    def concat_records(self):
        """
        Concatenate the recording segments into a final video
        """
        file_list = os.path.join(self.dir, "out.ffconcat")
        if not os.path.exists(file_list):
            self.logger.info(f"{file_list} was not found. Conversion failed.")
            return

        unique_file_list = os.path.join(self.dir, "out.unique.ffconcat")
        self.remove_duplicated_file(file_list, unique_file_list)

        cmd = ("ffmpeg -f concat -safe 0 -i " + unique_file_list +
               " -c copy -loglevel error " + os.path.join(self.dir, "record_screen.mp4"))

        subprocess.call(cmd, shell=True, stdout=PIPE,
                        stderr=PIPE, executable="/bin/bash")

    def stop_recording(self):
        """
        Stop the recording process
        """
        if self.process is not None:
            pgid = os.getpgid(self.process.pid)
            self.logger.info("kill recording process; pgid = " +
                             str(pgid) + ", pid = " + str(self.process.pid))
            try:
                os.killpg(pgid, signal.SIGTERM)
                self.process = None
            except Exception as e:
                self.logger.info("failed to kill the screen recording process:", str(e))


if __name__ == '__main__':
    duration = 10.0  # set recording duration in seconds
    sprit_num = 5
    dir = './movies'  # set save directory

    recorder = ScreenRecorder(dir, duration, sprit_num)
    recorder.start_recording()

    total_time = 35
    for i in range(total_time):
        print(f"{i+1:02d} / {total_time} [s] passed... ")
        time.sleep(1)

    recorder.stop_recording()

    recorder.concat_records()