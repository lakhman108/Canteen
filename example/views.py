# example/views.py
from datetime import datetime

from django.http import HttpResponse


def contanct(request):
    return HttpResponse("<h1>m name is lakhman</h1>")

def index(request):
    now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1>Hello from Vercel!</h1>
            <p>The current time is { now }.</p>
        </body>
    </html>
    '''
    return HttpResponse(html)