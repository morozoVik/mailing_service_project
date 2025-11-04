from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm
from django.http import JsonResponse
from .services import send_mailing_by_id


def index(request):
    """Главная страница"""
    if request.user.is_authenticated:
        total_mailings = Mailing.objects.filter(owner=request.user).count()
        active_mailings = Mailing.objects.filter(
            owner=request.user,
            status=Mailing.STATUS_STARTED
        ).count()
        unique_clients = Client.objects.filter(owner=request.user).count()
    else:
        total_mailings = 0
        active_mailings = 0
        unique_clients = 0

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_clients': unique_clients,
    }
    return render(request, 'mailing/index.html', context)


@login_required
def client_list(request):
    """Список клиентов"""
    clients = Client.objects.filter(owner=request.user)
    return render(request, 'mailing/client_list.html', {'clients': clients})


@login_required
def client_create(request):
    """Создание клиента"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.owner = request.user
            client.save()
            messages.success(request, 'Клиент успешно создан!')
            return redirect('mailing:client_list')
    else:
        form = ClientForm()
    return render(request, 'mailing/client_form.html', {'form': form})


@login_required
def client_update(request, pk):
    """Редактирование клиента"""
    client = get_object_or_404(Client, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Клиент успешно обновлен!')
            return redirect('mailing:client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'mailing/client_form.html', {'form': form})


@login_required
def client_delete(request, pk):
    """Удаление клиента"""
    client = get_object_or_404(Client, pk=pk, owner=request.user)
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Клиент успешно удален!')
        return redirect('mailing:client_list')
    return render(request, 'mailing/client_confirm_delete.html', {'client': client})


@login_required
def mailing_list(request):
    """Список рассылок"""
    mailings = Mailing.objects.filter(owner=request.user)
    return render(request, 'mailing/mailing_list.html', {'mailings': mailings})


@login_required
def mailing_create(request):
    """Создание рассылки"""
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.owner = request.user
            mailing.save()
            form.save_m2m()  # Сохраняем связи many-to-many
            messages.success(request, 'Рассылка успешно создана!')
            return redirect('mailing:mailing_list')
    else:
        form = MailingForm()
    return render(request, 'mailing/mailing_form.html', {'form': form})

@login_required
def message_list(request):
    """Список сообщений"""
    messages = Message.objects.filter(owner=request.user)
    return render(request, 'mailing/message_list.html', {'messages': messages})


@login_required
def message_create(request):
    """Создание сообщения"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.owner = request.user
            message.save()
            messages.success(request, 'Сообщение успешно создано!')
            return redirect('mailing:message_list')
    else:
        form = MessageForm()
    return render(request, 'mailing/message_form.html', {'form': form})


@login_required
def message_update(request, pk):
    """Редактирование сообщения"""
    message_obj = get_object_or_404(Message, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сообщение успешно обновлено!')
            return redirect('mailing:message_list')
    else:
        form = MessageForm(instance=message_obj)
    return render(request, 'mailing/message_form.html', {'form': form})


@login_required
def message_delete(request, pk):
    """Удаление сообщения"""
    message_obj = get_object_or_404(Message, pk=pk, owner=request.user)
    if request.method == 'POST':
        message_obj.delete()
        messages.success(request, 'Сообщение успешно удалено!')
        return redirect('mailing:message_list')
    return render(request, 'mailing/message_confirm_delete.html', {'message': message_obj})


@login_required
def mailing_update(request, pk):
    """Редактирование рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рассылка успешно обновлена!')
            return redirect('mailing:mailing_list')
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'mailing/mailing_form.html', {'form': form})


@login_required
def mailing_delete(request, pk):
    """Удаление рассылки"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    if request.method == 'POST':
        mailing.delete()
        messages.success(request, 'Рассылка успешно удалена!')
        return redirect('mailing:mailing_list')
    return render(request, 'mailing/mailing_confirm_delete.html', {'mailing': mailing})


@login_required
def mailing_send_now(request, pk):
    """Отправка рассылки по требованию через интерфейс"""
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

    if request.method == 'POST':
        try:
            successful, failed = send_mailing_by_id(pk)
            messages.success(
                request,
                f'Рассылка отправлена! Успешно: {successful}, Неудачно: {failed}'
            )
        except Exception as e:
            messages.error(request, f'Ошибка отправки: {str(e)}')

        return redirect('mailing:mailing_list')

    return render(request, 'mailing/mailing_send_confirm.html', {'mailing': mailing})