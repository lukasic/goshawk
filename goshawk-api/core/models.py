from django.db import models


class Collection(models.Model):
	acronym = models.CharField(max_length=20, unique=True)
	name = models.CharField(max_length=50, unique=True)
	description = models.TextField(blank=True, default="")
	default_ttl = models.IntegerField(default=0)

	def __str__(self):
		return self.acronym

	class Meta:
		ordering = ('acronym',)


class Reporter(models.Model):
	collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.name

	class Meta:
		ordering = ('collection', 'name',)


class List(models.Model):
	name = models.CharField(max_length=50)
	reporter = models.ManyToManyField(Reporter, blank=True)
	regex = models.TextField(blank=True, default="")
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.name

	class Meta:
		ordering = ('name',)


RECORD_POLICY = (
	('A', 'Allow'),
	('B', 'Block')
)


class Record(models.Model):
	list = models.ForeignKey(List, on_delete=models.CASCADE)
	reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)
	value = models.CharField(max_length=255)
	policy = models.CharField(max_length=1, choices=RECORD_POLICY)
	reason = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	expires_at = models.DateTimeField(null=True, blank=True)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.value

	class Meta:
		ordering = ('-created_at',)

