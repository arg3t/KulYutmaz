from mail import MailBox, Logger
import time
from threading import Thread
from subprocess import Popen, PIPE
import sys
import json

class MailWatcher(Thread):
	def __init__(self, account,  interval, creds, sensitivity, thresh, logger):
		Thread.__init__(self)
		self.account = account
		self.interval = interval
		self.threshold = thresh
		self.creds = creds
		self.sensitivity = sensitivity
		self.running = True
		self.stopped = False
		self.logger = logger

	def run(self):
		mailbox_obj = MailBox(self.account["uname"], self.account["password"], self.account["server"], self.account["port"],self.creds, self.sensitivity, self.threshold, self.logger)
		while 1 and self.running:
			time.sleep(self.interval/100)
			mailbox_obj.refresh_new_mails()

		self.stopped = True

	def stop(self):
		self.running = False

def thread_done(thread:MailWatcher):
	return thread.stopped

conf = json.loads(sys.stdin.readline())
workdir = sys.stdin.readline()

threads = []
loggers = []
mysql_creds = {}
main_log = Logger(workdir[:-1] + "/logs/main_process")
main_log.info("Started main process")

for i in conf:
	if i.startswith("mysql"):
		mysql_creds[i] = conf[i]

for i in conf["accounts"]:
	loggers.append(Logger(workdir[:-1] + "/logs/" + i["uname"]))
	threads.append(MailWatcher(i, conf["refresh_millis"], mysql_creds, conf["sensitivity"], conf["threshold"], loggers[-1]))
	threads[-1].start()

main_log.info("Created listeners")

while str(input()) != "0":
	continue
main_log.info("Detected interrupt. Stopping!")
for thread in threads:
	thread.stop()

main_log.info("Sent stop signal to all threads!")
while not all(map(thread_done,threads)):
	continue
main_log.info("All threads stopped!")

for logger in loggers:
	logger.stop()

exit(0)
