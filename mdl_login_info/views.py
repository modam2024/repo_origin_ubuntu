from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import CustomUserCreationForm  # 수정된 부분
# from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        # form = UserCreationForm(request.POST)
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f'Account created for {username}!')
            return redirect('login')  # 리디렉션할 페이지
    else:
        # form = UserCreationForm()
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
