import requests
import json
from database import DataBase
import time

ERRORS = {
	'CAPTCHA': 14,
	'INVALID_USER': 113
}
MINUTE = 60

class User:
	def __init__(self, json_object):
		self.user_id = json_object['user_id']
		self.user_number = json_object['user_number']
		self.phone_number = json_object['phone_number']
		self.token = json_object['token']
	def __str__(self):
		return 'User({}, {}, {}, {})'\
			.format(self.user_id, self.user_number, self.phone_number, self.token)
	def __repr__(self):
		return self.__str__()

class Bot:
	def __init__(self):
		self.accounts = []
		with open('config.json') as f:
			data = json.load(f)
			self.ACCESS_TOKEN = data['vk']['ACCESS_TOKEN']
			self.USERS_LIST_SIZE = int(data['vk']['USERS_LIST_SIZE'])
			for user in data['vk']['accounts']:
				self.accounts.append(User(user))
		print('token: {}'.format(self.ACCESS_TOKEN))
		print('size: {}'.format(self.USERS_LIST_SIZE))
		self.init_DB()
	def init_DB(self):
		self.db = DataBase()
	def get_all_users(self):
		return self.db.get_all()
	def add_all_with_timer(self, timer):
		users = self.get_all_users()
		for user in users:
			user_id = user[0]
			if '/' in user_id:
				user_id = user_id.split('/')[-1]
				print(user_id)
			if self.add(user_id):
				print('User {} added'.format(user_id))
				if self.db.update_friend_status(1, user_id):
					print('User friend status updated for user {}'.format(user_id))
			else:
				print('User {} was NOT added'.format(user_id))
			time.sleep(timer)
		return True
	def next_user(self):
		top_users = self.db.get_top()
		return top_users[0]
	def add_next(self):
		user = self.next_user()
		return self.add(user)
	def get_number_by_id(self, user_id, token=None):
		url = 'https://api.vk.com/method/users.get?user_ids={}&access_token={}&v=5.92'\
			.format(user_id, token if token else self.ACCESS_TOKEN)
		r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'})
		try:
			user_number = r.json()['response'][0]['id']
			return user_number
		except Exception as e:
			print('Ошибка получения id')
			error_code = r.json()['error']['error_code']
			print(r.json())
			if error_code == ERRORS['INVALID_USER']:
				print('User not exists')
			return False
	def add_with_status(self, user_number, token=None):
		url = 'https://api.vk.com/method/friends.add?user_id={}&access_token={}&v=5.92'\
			.format(user_number, token if token else self.ACCESS_TOKEN)
		r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'})
		try:
			status = r.json()['response']
			return status
		except Exception as e:
			error_code = r.json()['error']['error_code']
			print(r.json())
			status = error_code if not error_code in [1, 2, 4] else 0
			return status
	def add(self, user, token=None):
		print('Processing user {}'.format(user))
		user_number = self.get_number_by_id(user, token)
		status = self.add_with_status(user_number, token)

		if status in [1, 2, 4]:
			print('~~~~~~ ОГОНЬ ~~~~~~')
		else:
			if status == ERRORS['CAPTCHA']:
				print('Captcha')
			print('((( БРАТ НУ ТАК НЕ ПОЙДЕТ (((')
			return False
		return True
	def add_all_users(self):
		for account in self.accounts:
			print('ACCOUNT : {}\n'.format(account.user_id))
			user = self.next_user()[0]
			if self.add(user, token=account.token):
				self.db.update_friend_status(1, user)
			print('ACCOUNT PROCESSED\n')
			time.sleep(1)

if __name__ == '__main__':
	bot = Bot()
	bot.add_all_users()
	#bot.add(user=input('Input user: '))
	#bot.add_all_with_timer(30 * MINUTE)