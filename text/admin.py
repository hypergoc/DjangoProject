from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
import re
from .models import Text, TextCategory

@admin.register(TextCategory)
class TextCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'grade', 'status', 'short_content')
    list_filter = ('category', 'status')
    list_editable = ('grade',)
    search_fields = ('title', 'content', 'short_content')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add-texts/', self.admin_site.admin_view(self.add_texts_from_content_view), name='text_text_add_texts'),
        ]
        return custom_urls + urls

    def add_texts_from_content_view(self, request):
        if request.method == 'POST':
            raw_text = request.POST.get('raw_text', '')
            category_id = request.POST.get('category')
            category = None
            if category_id:
                try:
                    category = TextCategory.objects.get(pk=category_id)
                except TextCategory.DoesNotExist:
                    self.message_user(request, "Odabrana kategorija ne postoji.", level='error')
                    return redirect('.')

            entries = re.split(r'(?:\r\n|\n|\r)\s*(?:\r\n|\n|\r)+', raw_text.strip())

            counter = 1
            for entry in entries:
                counter +=1
                if not entry.strip():
                    continue


                if(counter % 2 == 0):
                    title = entry
                else:
                    short_content = entry.replace('Koncept:', '', 1).strip()
                    short_content = entry.replace('Manevar:', '', 1).strip()

                    obj, created = Text.objects.get_or_create(
                        title=title,
                        defaults={
                            'short_content': short_content,
                            'category': category
                        }
                    )

            return redirect('..')

        categories = TextCategory.objects.all()
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['categories'] = categories
        return render(request, 'admin/text/text/add_texts_form.html', context)