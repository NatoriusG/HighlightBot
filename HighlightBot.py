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
LOG = 'log.txt'

client = Bot(command_prefix=CLIENT_PREFIX)

# Write asynchronously to log file
async def log(message='', newline='\n', error=''):

	message += newline

	if error == 'warning':
		message = 'WARNING: ' + message
	elif error == 'fail':
		message = 'ERROR ' + message

	async with aiofiles.open(LOG, mode='a') as log_file:
		print(message, end='')
		await log_file.write(message)

# Take in a validated username and an image link, 
async def store(username, link):

	try:
		async with client.web_session.get(link, headers=IMG_HEAD) as web_response:
			print('response:\n{}'.format(await web_response.json()))
	except:
		await log('accessing web content failed for link: {}'.format(link), 'fail')
		return


		
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