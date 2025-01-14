from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

@login_required
@user_passes_test(lambda u: u.groups.filter(name="organisers").count())
def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')
