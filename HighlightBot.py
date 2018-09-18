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
STORE_PATH = 'userdata/{}.nes'
LOG = 'log.txt'
LOG_ON = False

client = Bot(command_prefix=CLIENT_PREFIX)

# Write asynchronously to log file
async def log(message='', newline='\n', error=''):

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

	print('getting tags')
	return [ 'test', 'test2', 'testing' ]
	#try:
	#	async with client.web_session.get(link, headers=IMG_HEAD) as web_response:
	#		print('response:\n{}'.format(await web_response.json()))
	#except:
	#	await log('accessing web content failed for link: {}'.format(link), 'fail')
	#	return

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

	stored_data.append(register_data)
	merged_data = yaml.dump(stored_data)
	print('merged data: {}'.format(merged_data))

	# Finally, write to file
	async with aiofiles.open(STORE_PATH.format(username), mode='w') as userdata_file:
		await userdata_file.write(merged_data)
		await userdata_file.flush()
		
@client.command(name='register',
				description='Registers a higlight link with the user mentioned.',
				brief='Show-off.',
				aliases=['r'])
async def register(*args):
	username = None
	link = None

	# Initial parsing
	for argument in args:
		if argument.startswith('player=') or argument.startswith('user='):
			username = argument.split('=')[1]
		elif argument.startswith('link=') or argument.startswith('highlight='):
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
		await store(username, link)
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