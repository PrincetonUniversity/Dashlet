import json

fd = open('sample.json')
data = json.load(fd)


lists = data['data']


for i in range(len(lists)):

	video_entry = lists[i]['aweme_info']['video']

	print(video_entry['duration'])

	print(video_entry['play_addr']['uri'])

	# print(video_entry['play_addr']['url_list'][0])

	# print(video_entry['bit_rate'][0]['play_addr']['url_list'][0])


	print(len(video_entry['bit_rate']))

	bit_rates = []
	uri_hash = []

	for j in range(len(video_entry['bit_rate'])):
		# print(video_entry['bit_rate'][j]['bit_rate'])

		bit_rates.append(str(video_entry['bit_rate'][j]['bit_rate']))

		url0 = video_entry['bit_rate'][j]['play_addr']['url_list'][0]
		url1 = video_entry['bit_rate'][j]['play_addr']['url_list'][1]


		entrys0 = url0.split("/")
		entrys1 = url1.split("/")

		# print(entrys0[3])
		# print(entrys1[3])

		uri_hash.append(entrys0[3])
		uri_hash.append(entrys1[3])

	print("&".join(bit_rates))
	print("&".join(uri_hash))

		# print(video_entry['bit_rate'][j]['bit_rate'])

	# print(video_entry['bit_rate'][0]['bit_rate'])

	# print(video_entry['bit_rate'][1]['play_addr']['url_list'][0])

	# print(video_entry['bit_rate'][1]['bit_rate'])


	
tmp = 1