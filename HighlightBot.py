from discord.ext.commands import Bot
import aiohttp
import yaml

CLIENT_PREFIX = 'h!'
with open('.token') as token_file:
	TOKEN = token_file.readline()

client = Bot(command_prefix=CLIENT_PREFIX)

# Take in a validated username and an image link, 
async def store(username, link):

	with client.web_session.get(link) as web_response:
		print('response:\n{}'.format(web_response))
		
@client.command(name='register',
				description='Registers a higlight link with the user mentioned.',
				brief='Show-off.',
				aliases=['register', 'r'],
				pass_context=True)
async def register(*args):
	username = None
	link = None

	# Initial parsing
	for argument in args:
		if argument.startswith('player:') or argument.startswith('user:'):
			username = argument.split(':')[1]
			print('user found: {}'.format(user))
		elif argument.startswith('link:') or argument.startswith('highlight:'):
			link = argument.split(':')[1]

	# Data validation
	# TODO: validate link
	valid = False
	for user in client.users:
		if username == user.name:
			valid = True

	if valid == True:
		store(username, link)
	else:
		print('store failed: invalid arguments')
		await client.say('Link register failed: invalid arguments.')

@client.event
async def on_ready():

	# Setup web session
	client.web_session = aiohttp.ClientSession(loop=client.loop)

	# Register a list of all users this bot can see
	client.users = []
	for server in client.servers:
		for member in server.members:
			client.users.append(member)

	print('Setup finished, {} is now online.'.format(client.user.name))
	print('---------------------------------------------')