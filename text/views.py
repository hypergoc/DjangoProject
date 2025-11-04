from django.shortcuts import render
from .models import Text
import re

# Create your views here.
def add_texts_view(request):
    print(request)
    context = {}
    if request.method == 'POST':
        raw_text = request.POST.get('raw_text', '')
        # Split by one or more blank lines
        entries = re.split(r'\n\s*\n', raw_text.strip())
        created_count = 0
        
        for entry in entries:
            if not entry.strip():
                continue

            lines = entry.strip().split('\n')
            
            if len(lines) >= 2:
                title = lines[0].strip()
                content_line = lines[1].strip()

                if title and content_line.startswith('Koncept:'):
                    short_content = content_line.replace('Koncept: ', '', 1).strip()
                    
                    # Using get_or_create to avoid creating duplicates based on the title
                    obj, created = Text.objects.get_or_create(
                        title=title,
                        defaults={
                            'short_content': short_content,
                            'content': short_content 
                        }
                    )
                    if created:
                        created_count += 1
        
        context['success_message'] = f'Uspješno stvoreno {created_count} novih zapisa.'

    return render(request, 'text/add_texts.html', context)