from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import datetime, timedelta
from django.contrib.auth.models import User


from profiles.models import *

fake = Faker('en_US')

class Command(BaseCommand):

	def country(self):
		try:
			country = Country.objects.get(name="Zimbabwe")
		except:
			self.stdout.write(self.style.NOTICE('Adding Country'))
			country = Country.objects.create(name="Zimbabwe")
			country.save()
		return country

	def cities(self):
		_cities = {
			1:{
				'name': 'Harare',
				'abb': 'HRE'
			},
			2:{
				'name': 'Bulawayo' ,
				'abb': 'BYO'
			},
			3:{
				'name': 'Chitungwiza',
				'abb': 'CTG'
			},
			4:{
				'name': 'Mutare',
				'abb': 'MTR'
			},
			5:{
				'name': 'Victoria Falls',
				'abb': 'VCF'
			},
			6:{
				'name': 'Gweru',
				'abb': 'GWE'
			},
			7:{
				'name': 'Kwekwe',
				'abb': 'KKW'
			},
			8:{
				'name': 'Kadoma',
				'abb': 'KDM'
			},
			9:{
				'name': 'Masvingo',
				'abb': 'MSV'
			},
			10:{
				'name': 'Chinhoyi',
				'abb': 'CNH'
			},
			11:{
				'name': 'Norton',
				'abb': 'NRT'
			},
			12:{
				'name': 'Marondera',
				'abb': 'MRD'
			},
			13:{
				'name': 'Ruwa',
				'abb': 'RUW'
			},
			14:{
				'name': 'Chegutu',
				'abb': 'CGT'
			},
			15:{
				'name': 'Zvishavane',
				'abb': 'ZVS'
			},
			16:{
				'name': 'Bindura',
				'abb': 'BND'
			},
			17:{
				'name': 'Beitbridge',
				'abb': 'BBG'
			},
			18:{
				'name': 'Redcliff',
				'abb': 'RDC'
			},
			19:{
				'name': 'Rusape',
				'abb': 'RUS'
			},
			20:{
				'name': 'Kariba',
				'abb': 'KBA'
			}
		}
		country = self.country()
		for k, _city in _cities.items():
			try:
				City.objects.get(country=country, name=_city['name'])
			except:
				self.stdout.write(self.style.NOTICE(f'Adding city {_city["name"]}'))
				City.objects.create(country=country, name=_city['name'], abbreviation=_city['abb']).save()

	def offices(self):
		_offices = [
			{
				'name': 'Office 1',
				'abb': 'OF1'			
			},{
				'name': 'Office 2',
				'abb': 'OF2'			
			},{
				'name': 'Office 3',
				'abb': 'OF3'			
			}
		]
		n_offices = random.choice([1,2,3]) # possible number of offices a city can have
		country = self.country()
		cities = City.objects.all()
		for city in cities:
			subset = random.sample(list(_offices), random.choice(range(1,len(_offices)+1)))
			for i, office in enumerate(subset):
				try:
					Office.objects.get(name=office['name'], city=city)
				except:
					self.stdout.write(self.style.NOTICE(f'Adding office {office["name"]} in {city.name}'))
					Office.objects.create(name=office['name'], code=office['abb'], country=country, city=city).save()


	def departments(self):
		_departments = {
			1:{
				'name': 'Accounting',
				'abb': 'ACC'			
			},
			2:{
				'name': 'Finance',
				'abb': 'FIN'			
			},
			3:{
				'name': 'Human Resources',
				'abb': 'HRS'			
			},
			4:{
				'name': 'Information Technology',
				'abb': 'ITS'			
			},
			5:{
				'name': 'Transport and Logistics',
				'abb': 'TAL'			
			}
		}
		country = self.country()
		offices = Office.objects.all()
		for office in offices:
			for i, dept in _departments.items():
				try:
					Department.objects.get(name=dept['name'], city=office.city, office=office, country=office.city.country)
				except:
					self.stdout.write(self.style.NOTICE(f'Adding Department {dept["name"]} in {office.name} under {office.city.name}'))
					Department.objects.create(name=dept['name'], code=dept['abb'], city=office.city, office=office, country=office.city.country).save()

	def levels(self):
		for level in range(10):
			name = f"Level {level}"
			try:
				Level.objects.get(name=name, level=level)
			except:
				self.stdout.write(self.style.NOTICE(f'Adding Level {level}'))
				Level.objects.create(level=level, name=name).save()

	def gen_phone(self):
	    first = str(random.randint(100,999))
	    second = str(random.randint(1,888)).zfill(3)
	    last = (str(random.randint(1,9998)).zfill(4))
	    while last in ['1111','2222','3333','4444','5555','6666','7777','8888']:
	        last = (str(random.randint(1,9998)).zfill(4))

	    return '{}-{}-{}'.format(first,second, last)

	def users(self):
		for count in range(200):
			department=random.choice(Department.objects.all())
			f_name,l_name = fake.name().split(" ", 1)
			username = f_name.lower()
			try:
				User.objects.get(username=username)
			except:
				self.stdout.write(self.style.NOTICE(f'Adding User {f_name}'))
				user = User.objects.create_user(username=username, email=f'{username}@mail.com', password='password12345')
				user.first_name = f_name
				user.last_name = l_name
				user.save()
			
			self.stdout.write(self.style.NOTICE(f" updating {f_name}'s profile"))
			profile = UserProfile.objects.get(user=user)
			profile.title=fake.job()
			profile.phone=self.gen_phone()
			profile.department=department
			profile.office=department.office
			profile.city=department.office.city
			profile.level=random.choice(Level.objects.all())
			profile.save()

	def handle(self, *args, **kwargs):
		country = self.country()
		del country
		cities = self.cities()
		del cities
		offices = self.offices()
		del offices
		departments = self.departments()
		del departments
		levels = self.levels()
		del levels
		users = self.users()
		del users
		self.stdout.write(self.style.SUCCESS('DONE: profiles app was successfuly populated'))
