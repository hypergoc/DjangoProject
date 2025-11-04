from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
import re
from .models import Text

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'short_content')
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

            entries = re.split(r'(?:\r\n|\n|\r)\s*(?:\r\n|\n|\r)+', raw_text.strip())
            counter = 1

            for entry in entries:
                counter += 1
                if not entry.strip():
                    continue

                if(counter % 2 == 0):
                    title = entry
                else:
                    short_content = entry.replace('Koncept:', '', 1).strip()

                    obj, created = Text.objects.get_or_create(
                        title=title,
                        defaults={
                            'short_content': short_content
                        }
                    )

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        return render(request, 'admin/text/text/add_texts_form.html', context)