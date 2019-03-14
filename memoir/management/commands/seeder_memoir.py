from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import datetime, timedelta
from django.contrib.auth.models import User

from profiles.models import *
from memoir.models import *
from django.db.models import Max
from memoir.utils import *

fake = Faker('en_US')



class Command(BaseCommand):
	def random_date(self):
		start = datetime.strptime('1/1/2010','%m/%d/%Y')
		end = datetime.now()
		"""Generate a random datetime between `start` and `end`"""
		return start + timedelta(
			# Get a random amount of seconds between `start` and `end`
			seconds=random.randint(0, int((end - start).total_seconds())),
		)

	def memos(self):
		users = User.objects.all().exclude(username='admin')
		users = users.exclude(username="AnonymousUser")
		for i in range(20): #specify the number of memos to be created
			sender = random.choice(users)
			try:
				ref_num = get_ref_number(sender)
			except:
				sender = random.choice(users) # find another user
				ref_num = get_ref_number(sender)

			try:
				memo = Memo.objects.get(reference_number=ref_num)
			except:	
				poss_rec = users.exclude(username=sender.username)
				poss_rec = poss_rec.filter(user_profile__level__gte=sender.user_profile.level.level)
				n_rec = random.choice(range(1,len(poss_rec)))
				if n_rec > 10:					
					subset = random.sample(list(poss_rec), random.choice(range(1,10)))
				else:
					subset = random.sample(list(poss_rec),  random.choice(range(1,10)))

				message = ''
				paragraphs_list = fake.paragraphs(random.choice(range(1,20)))
				for k, v in enumerate(paragraphs_list):
					message+=f" {v}"

				memo = Memo.objects.create(
						sender=sender,
						subject=fake.sentence(),
						message=message,
						reference_number=ref_num,
						created=self.random_date()
					)
				memo.save()
				
				self.stdout.write(self.style.NOTICE(f'Created Memo {i}: {memo.reference_number}'))	

				for rec in subset:
					memo.recipients.add(rec)
					poss_rec = poss_rec.exclude(username=rec.username)
				poss_to_lvl = poss_rec.aggregate(largest=Max('user_profile__level'))['largest']

				if poss_to_lvl > sender.user_profile.level.level:
					poss_to = poss_rec.filter(user_profile__level__gte=poss_to_lvl)
					to = random.choice(poss_to)
					memo.to = to
					memo.save()
				else:
					pass

	def send_memos(self):
		memos = Memo.objects.all()
		subset = random.sample(list(memos), round(0.95*len(memos)))
		for memo in subset:
			self.stdout.write(self.style.NOTICE(f'Sending Memo {memo.reference_number}'))		
			memo.sent = True
			memo.save()

	def archive_memos(self):
		memos = Memo.objects.all().filter(sent=True)
		subset = random.sample(list(memos), round(0.75*len(memos)))
		for memo in subset:
			self.stdout.write(self.style.NOTICE(f'Archiving Memo {memo.reference_number}'))
			if memo.to:		
				Archive.objects.create(memo=memo, archived=True, archiver=memo.to).save()

	def request_fuel(self):
		memos = Memo.objects.all().filter(sent=True)
		subset = random.sample(list(memos), round(0.60*len(memos)))
		types = ['Petrol', 'Diesel']
		priotities = ['Normal', 'High']
		amounts = range(5, 100)
		for memo in subset:
			self.stdout.write(self.style.NOTICE(f'Adding Fuel Request for Memo {memo.reference_number}'))
			Fuel.objects.create(
					memo=memo, 
					priority=random.choice(priotities), 
					fuel_type=random.choice(types), 
					amount=random.choice(amounts),
					office=memo.sender.user_profile.department.office,
					department=memo.sender.user_profile.department,
					city=memo.sender.user_profile.department.office.city,
					date_requested=memo.created,
				).save()

	def comments(self):
		memos = Memo.objects.all().filter(sent=True)
		subset = random.sample(list(memos), round(0.80*len(memos)))
		for _memo in subset:
			recipients = _memo.recipients.all().order_by('user_profile__level')
			rec_subset = random.sample(list(recipients), round(0.80*len(recipients)))
			for re in rec_subset:
				comment = MemoComment.objects.create(
						memo=_memo,
						comment=random.choice([fake.sentence(),fake.text()]),
						commenter=re
					)
				comment.save()
				self.stdout.write(self.style.NOTICE(f'{re} added a comment to Memo {_memo.reference_number}'))


	def handle(self, *args, **kwargs):
		memos = self.memos()
		del memos
		# sent = self.send_memos()
		# del sent
		# request_fuel = self.request_fuel()
		# del request_fuel
		# commnts = self.comments()
		# del commnts
		# archive = self.archive_memos()
		# del archive
		self.stdout.write(self.style.SUCCESS('DONE: memoir app was successfuly populated'))
