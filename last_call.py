#!/usr/bin/python3

import csv
import requests

#open Scan Queue csv file, return json 
with open('vss.csv', 'r') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for row in reader:
		print(row[0])
		print(row[1])
