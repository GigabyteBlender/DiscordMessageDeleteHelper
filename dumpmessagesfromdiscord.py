import json
import os
from typing import Dict, List
import re

class dumpallmessages():
	def save_messages(self, messages: Dict[str, List[int]]):
		print('creating file...')
		#change the directory to where you want to create the file/open
		with open(r"/Users/dpertu/Documents/messages.txt", "w+") as f:
			for channel in messages.items():
				print(f'Saving messages from channel: {channel}')
				channel = re.sub('[^A-Za-z0-9]+','', str(channel))
				float(channel)
				f.write(f'{channel}:\n\n')
	
				for ids in messages.items():
					for id in ids:
						id = re.sub('[^A-Za-z0-9]+', '', str(id))
						if id != '':
							float(id)
							f.write(f'{id}, ')
				f.write('\n\n')

	def dump_dir(self, path: str) -> List[int]:
		messages = []
		if not os.path.isdir(path):
			return messages

		if not os.path.exists(f'{path}/messages.json'):
			print(f'No messages found in: {path}')
			return messages

		print(f'Dumping messages from: {path}')
		with open(f'{path}/messages.json', 'r', encoding='utf8') as f:
			messages_obj = json.load(f)
			for message in messages_obj:
				messages.append(message['ID'])

		return messages

	def dump_all(self) -> Dict[str, List[int]]:
		messages = {}
		#change the directory to where the messages folder is from the discord package
		for channel in os.listdir(r"/Users/dpertu/Documents/package/messages"):
			path = f'messages/{channel}'

			channel_id = channel.replace('c', '', 1)
			messages[channel_id] = self.dump_dir(path)

		return messages

	def main(self):
		messages = self.dump_all()
		self.save_messages(messages)

if __name__ == "__main__":
    
	main = dumpallmessages()
	main.main()

	print("Dumped to messages.csv!")
