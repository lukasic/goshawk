from django.contrib import admin

from core.models import Collection, Reporter, List, Record

class CollectionAdmin(admin.ModelAdmin):
	list_display = ["acronym", "name", "description", "default_ttl"]
	search_fields = ["acronym", "name", "description"]

class ReporterAdmin(admin.ModelAdmin):
	list_display = [ "name", "collection", "active" ]
	list_filter = [ "collection", "active" ]
	search_fields = ["name",]

class ListAdmin(admin.ModelAdmin):
	list_display = [ "name", "regex", "active" ]
	list_filter = [ "reporter", "active" ]
	search_fields = ["name",]
#	filter_horizontal = ["reporter", ]

class RecordAdmin(admin.ModelAdmin):
	list_display = ["value", "policy", "reporter", "list", "reason", "created_at", "expires_at", "active"]
	list_filter = ["active", "policy", "reporter", "list"]
	search_fields = ["value", "reason"]


admin.site.register(Collection, CollectionAdmin)
admin.site.register(Reporter, ReporterAdmin)
admin.site.register(List, ListAdmin)
admin.site.register(Record, RecordAdmin)
