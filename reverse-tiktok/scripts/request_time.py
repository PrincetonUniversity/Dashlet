import csv



IDX_REQUEST_START = 2
IDX_REQUEST_END = 3
IDX_RESPONSE_START = 4
IDX_RESPONSE_END = 5

IDX_IDENTIFYER = 7

table_list = []

with open('cooked-low.csv', newline='') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

	for row in spamreader:
		table_list.append(row)
	

for i in range(1, len(table_list)):
	row = table_list[i]
	row_pre = table_list[i-1]

	# print(row_pre[IDX_RESPONSE_END])

	if row_pre[IDX_RESPONSE_END] != " None":
		print(row[IDX_IDENTIFYER], float(row[IDX_REQUEST_START]) - float(row_pre[IDX_RESPONSE_END]))
