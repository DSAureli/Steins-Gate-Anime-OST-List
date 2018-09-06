import json

with open("S;G_OST.json") as f:
	data = json.load(f)

text = '''
{| class="article-table mw-collapsible mw-collapsed"
|+ class="nowrap" | Per-episode
|-
! style="text-align: center;" |Ep
! style="text-align: center;" |Time
! style="text-align: center;" |Title
! style="text-align: center;" |Comment
! style="text-align: center;" |Scene
'''

for ep in data:
	
	text += '|-\n'
	text += '| rowspan="{}" style="text-align: center;"|{}\n'.format(len(ep['tracks']), ep['number'])
	
	for idx,track in enumerate(ep['tracks']):
		
		if idx != 0:
			text += '|-\n'
		
		for _,val in track.items():
			
			text += '| style="text-align: center;"|{}\n'.format(val)
	
text += '|}'

with open("wikitable.txt", "w") as file:
	file.write(text)
