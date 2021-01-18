from django.contrib import admin

from .models import Image

# Register your models here.
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    '''Admin View for Image'''

    list_display = ('title', 'properties', 'colors', 'photo', 'private', 'owner', 'created', )
    list_filter = ('created', 'private',)
    # inlines = [
    #     Inline,
    # ]
    # raw_id_fields = ('',)
    # readonly_fields = ('',)
    search_fields = ('title', 'properties', 'colors',)
    date_hierarchy = 'created'
    # ordering = ('',)