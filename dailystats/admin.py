from django.contrib import admin
from django.contrib.auth.models import Permission, User
from .models import AmountModel, Measure, Category

""" class ChoiceInlineTwo(admin.TabularInline):
    model = MeasureFields
    extra = 10
    
class MeasureFieldsAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['category_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('category_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['category_text']
 """

    

""" admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubcategoryAdmin) """
admin.site.register(AmountModel)
admin.site.register(Measure)
admin.site.register(Category)
