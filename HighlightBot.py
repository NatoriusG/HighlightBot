from discord.ext.commands import Bot
import aiofiles
import aiohttp
import json
import yaml

CLIENT_PREFIX = 'h!'
with open('.tokens') as token_file:
	TOKEN = token_file.readline().rstrip('\n')
	IMG_ID = token_file.readline().rstrip('\n')
IMG_HEAD = { 'Authorization': 'Client-ID {}'.format(IMG_ID) }
IMG_URL = 'https://api.imgur.com/3/album/{}'
STORE_PATH = 'userdata/{}.nes'
LOG = 'log.txt'
LOG_ON = False

client = Bot(command_prefix=CLIENT_PREFIX)

# Write asynchronously to log file
async def log(message='', error='', newline='\n'):

	message += newline

	if error == 'warn':
		message = 'WARNING: ' + message
	elif error == 'fail':
		message = 'ERROR ' + message

	async with aiofiles.open(LOG, mode='a') as log_file:
		print(message, end='')
		if LOG_ON == True:
			await log_file.write(message)

async def get_tags(link):

	# Get correct url
	album_id = link[link.rfind('/')+1:]
	album_url = IMG_URL.format(album_id)

	# Request data and find tags
	tags = []

	try:
		async with client.web_session.get(link, headers=IMG_HEAD) as web_response:

			image_data = (await web_response.json())['data']['images'][0]
			tags = image_data['description'].replace(' ', '').split('#')[1:]

	except:
		await log('accessing web content failed for link: {}'.format(link), 'fail')

	return tags

# Take in a validated username and an image link, 
async def store(username, link):

	tags = await get_tags(link)
	register_data = { 'link': link, 'tags': tags }

	# First collect any stored data
	stored_data = None

	try:
		async with aiofiles.open(STORE_PATH.format(username), mode='r') as userdata_file:
			stored_data = yaml.load(await userdata_file.read())
	except:
		await log('Failed to open userdata file for user: {}'.format(username), 'warn')

	# Now merge in new data
	if stored_data == None:
		stored_data = []
	else:
		for data_entry in stored_data:
			# If the new data is a copy of some old data, throw it away
			if data_entry == register_data:
				await log('Data found to be duplicate, ignoring', 'warn')
				register_data = None

	if register_data != None:
		stored_data.append(register_data)

	merged_data = yaml.dump(stored_data)
	print('merged data: {}'.format(merged_data))

	# Finally, write to file
	async with aiofiles.open(STORE_PATH.format(username), mode='w') as userdata_file:
		await userdata_file.write(merged_data)
		await userdata_file.flush()

	# Inform command of result
	if register_data != None:
		return 'success'
	else:
		return 'duplicate'
		
@client.command(name='register',
				description='Registers a higlight link with the user mentioned.',
				brief='Show-off.',
				aliases=['r'])
async def register(*args):
	username = None
	link = None

	# Initial parsing
	for argument in args:
		if argument.startswith('player=') or argument.startswith('user=') or argument.startswith('u='):
			username = argument.split('=')[1]
		elif argument.startswith('link=') or argument.startswith('highlight=') or argument.startswith('l='):
			link = argument.split('=')[1]

	await log('user is {}, link is {}'.format(username, link))

	# Data validation
	# TODO: validate link
	valid = False
	for user in client.users:
		if username == user.name:
			await log('username {} matches known name'.format(username))
			valid = True
			
	if valid == True:

		result = await store(username, link)
		
		if result == 'success':
			await client.say('New highlight for {} stored successfully.'.format(username))
		elif result == 'duplicate':
			await client.say('Highlight for {} was already stored.'.format(username))
	else:
		await log('invalid arguments: [ {}, {} ]'.format(username, link), 'fail')

@client.event
async def on_ready():

	# Setup web session
	client.web_session = aiohttp.ClientSession(loop=client.loop)

	# Register a list of all users this bot can see
	client.users = []
	for server in client.servers:
		for member in server.members:
			client.users.append(member)

	await log('Setup finished, {} is now online.'.format(client.user.name))
	await log('ID: {}'.format(client.user.id))
	await log('Token: {}'.format(TOKEN))
	await log('Client ID for Imgur: {}'.format(IMG_ID))
	await log()

client.run(TOKEN)