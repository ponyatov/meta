# \ <section:top>
from django import forms
from .models import *
# / <section:top>
# \ <section:mid>
import datetime as dt
class bullyForm(forms.Form):
    date = forms.DateField(
        initial = dt.date.today(),
        widget= forms.SelectDateWidget(
            
        )
        
    )
# / <section:mid>
