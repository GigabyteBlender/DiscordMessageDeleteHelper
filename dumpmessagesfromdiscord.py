import json
import os
from typing import Dict, List
import re

def save_messages(messages: Dict[str, List[int]]):
	print('creating file...')
	with open(r"C:\Users\danpe\Downloads\messages.csv", "w+", encoding='utf8') as f:
		f.write('channelid,messageid\n')
		for channel in messages.items():
			channel = re.sub('[^A-Za-z0-9]+','', str(channel))
			channel.strip()
			print(f'Saving messages from channel: {channel}')
			for ids in messages.items():
				for id in ids:
					id = re.sub('[^A-Za-z0-9]+', '', str(id))
					id.strip()
					if id != '':
						float(id)
						float(channel)
						f.write(f'{channel},{id}\n')
		f.close()

def dump_dir(path: str) -> List[int]:
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

def dump_all() -> Dict[str, List[int]]:
	messages = {}
	for channel in os.listdir(r"C:\Users\danpe\Downloads\package\messages"):
		path = f'messages/{channel}'

		channel_id = channel.replace('c', '', 1)
		messages[channel_id] = dump_dir(path)

	return messages

def main():
	messages = dump_all()
	save_messages(messages)

if __name__ == "__main__":
	main()
	print("Dumped to messages.csv!")
