from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import User
from friendship.models import Friend, FriendshipRequest
from django.contrib.auth.decorators import login_required

from .forms import UserCreateForm, AddFriendForm, MakeMessageForm
from .models import Message
from purchase_log.models import Receipt, ShareNotification


def get_common_context(user, receipt_id=None):
    # Retrieves commonly re-used data for certain views.
    common_context = {}
    receipt_list = []  # Always in common_context
    total_dict = {}  # Always in common_context
    num_of_new_friend_requests = len(Friend.objects.unread_requests(user=user))
    new_messages = [message for message in Message.objects.filter(to_user=user) if message.read is False]
    new_share_notifications = [
        notification for notification in ShareNotification.objects.filter(
            to_user=user,
            read=False
        )
    ]
    num_of_new_messages = len(new_messages)
    num_of_new_share_notifications = len(new_share_notifications)
    common_context['num_of_new_friend_requests'] = num_of_new_friend_requests
    common_context['num_of_new_messages'] = num_of_new_messages
    common_context['num_of_new_share_notifications'] = num_of_new_share_notifications
    common_context['total_new_notifications'] = num_of_new_share_notifications + num_of_new_messages + num_of_new_friend_requests
    description = ''
    for receipt in Receipt.objects.all():
        if receipt.owner == user:
            receipt_list.append(receipt)
            temp_list = [item.price for item in receipt.receiptproduct_set.all()]
            taxed_items = [item.price for item in receipt.receiptproduct_set.all() if item.tax]
            total_dict[receipt.id] = format(((sum(taxed_items)*receipt.tax)+(sum(temp_list))), '.2f')
            common_context["total_dict"] = total_dict
            common_context["receipt_list"] = receipt_list
    if receipt_id:
        current_receipt = get_object_or_404(Receipt, pk=receipt_id)
        # Creates a set of users tagged in a receipt
        list_of_purchasers = [item.shareitem_set.all() for item in current_receipt.receiptproduct_set.filter(split=True)]
        if current_receipt.owner != user and user not in set([share_item.purchasers for share_item in list_of_purchasers[0]]):
            raise Http404
        items = current_receipt.receiptproduct_set.all()
        for item in items:
            if item.description == 'None':
                description = ''
            else:
                description = item.description
        total = sum([item.price for item in items])
        taxed_items = [item.price for item in items if item.tax]
        tax = (sum(taxed_items)*current_receipt.tax)
        total_and_tax = (total + tax)
        common_context['total'] = ("%.2f" % total)
        common_context['tax'] = ("%.2f" % tax)
        common_context['current_receipt'] = current_receipt
        common_context['items'] = items
        common_context['total_and_tax'] = ("%.2f" % total_and_tax)
        common_context['description'] = description
    return common_context


def logout_view(request):
    """Log the user out."""
    logout(request)
    return HttpResponseRedirect(reverse('purchase_log:index'))


def register(request):
    """Register a new user."""
    if request.method != 'POST':
        # Display blank registration form.   
        form = UserCreateForm()
    else:
        # Process completed form.
        form = UserCreateForm(data=request.POST)
        
        if form.is_valid():
            new_user = form.save()
            # Log the user in, and then redirect to home page.
            authenticated_user = authenticate(username=new_user.username,
                password=request.POST['password1'])
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse('index:index'))

    context = {'form': form}
    return render(request, 'users/register.html', context)


def friends(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    friend_list = [friend for friend in Friend.objects.friends(request.user)]
    context = {
        'user': user,
        'friend_list': friend_list,
    }
    common_context = get_common_context(request.user)
    for key, value in common_context.items():
        context[key] = value
    return render(request, 'users/friends.html', context)


@login_required
def add_friend(request):
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = AddFriendForm
        status_message = ''
    else:
        # POST data submitted; process data.
        form = AddFriendForm(data=request.POST)
        status_message = ''
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if email not in [user.email for user in User.objects.all()]:
                status_message = 'No user with that email.'
            else:
                r_list = [f_request for f_request in Friend.objects.unrejected_requests(user=User.objects.get(email=email))
                          if f_request.from_user == request.user]

                if email == request.user.email:
                    status_message = 'You cannot add yourself as a friend.'
                elif len(r_list) >= 1:
                    status_message = 'You have already sent a request to that user.'
                elif Friend.objects.are_friends(request.user, User.objects.get(email=email)):
                    status_message = 'You are already friends with ' + User.objects.get(email=email).username + '.'
                else:
                    status_message = 'Friend request sent!'

        if form.is_valid() and status_message == 'Friend request sent!':
            email = form.cleaned_data.get('email')
            other_user = User.objects.get(email=email)
            Friend.objects.add_friend(
                request.user,                               # The sender
                other_user,                                 # The recipient
                message='Hi! I would like to add you')
    context = {'form': form, 'status_message': status_message}
    common_context = get_common_context(request.user)
    for key, value in common_context.items():
        context[key] = value
    return render(request, 'users/add_friend_form.html', context)


def inbox(request, user_id):
    user = User.objects.get(pk=user_id)
    if user != request.user:
        raise Http404

    message_list = [message for message in Message.objects.filter(to_user=User.objects.get(pk=user_id))]
    context = {
        'message_list': message_list
    }
    common_context = get_common_context(request.user)
    for key, value in common_context.items():
        context[key] = value
    return render(request, 'users/inbox.html', context)


def sent_messages(request, user_id):
    if User.objects.get(pk=user_id) != request.user:
        raise Http404
    else:
        message_list = [message for message in Message.objects.filter(from_user=User.objects.get(pk=user_id))]
        context = {
            'message_list': message_list
        }
        common_context = get_common_context(request.user)
        for key, value in common_context.items():
            context[key] = value
        return render(request, 'users/sent_messages.html', context)


def message_details(request, message_id):
    current_message = Message.objects.get(pk=message_id)
    if current_message.to_user != request.user:
        message = Message.objects.get(pk=message_id)
    else:
        message = Message.objects.read_message(message_id)
    context = {
        'message': message,
        'user': request.user,
    }
    common_context = get_common_context(request.user)
    for key, value in common_context.items():
        context[key] = value
    return render(request, 'users/message_details.html', context)


@login_required
def friend_requests(request, user_id):
    user = User.objects.get(pk=user_id)
    if user != request.user:
        raise Http404
    else:
        unread_friend_request_list = [request for request in
                                      Friend.objects.unread_requests(user=request.user)]
        read_friend_request_list = [request for request in
                                    Friend.objects.unrejected_requests(user=request.user)
                                    if request not in unread_friend_request_list]
    context = {
    'unread_friend_request_list': unread_friend_request_list,
    'read_friend_request_list': read_friend_request_list,
    }
    common_context = get_common_context(request.user)
    for key, value in common_context.items():
        context[key] = value
    return render(request, 'users/friend_request.html', context)


def request_details(request, f_request_id):
    f_request = FriendshipRequest.objects.get(pk=f_request_id)
    f_request.mark_viewed()
    context = {
        'f_request': f_request,
    }
    common_context = get_common_context(request.user)
    for key, value in common_context.items():
        context[key] = value
    return render(request, 'users/f_request_details.html', context)


def accept_request(request, f_request_id):
    f_request = FriendshipRequest.objects.get(pk=f_request_id)
    f_request.accept()
    return HttpResponseRedirect(reverse('users:inbox', args=[request.user.id]))


def decline_request(request, f_request_id):
    f_request = FriendshipRequest.objects.get(pk=f_request_id)
    f_request.reject()
    return HttpResponseRedirect(reverse('users:inbox', args=[request.user.id]))


def ignore_request(request, f_request_to_user_id):
    return HttpResponseRedirect(reverse('users:inbox', args=[request.user.id]))


def delete_friend(request, friend_id):
    Friend.objects.remove_friend(request.user, User.objects.get(id=friend_id))
    return HttpResponseRedirect(reverse('users:friends', args=[request.user.id]))


@login_required
def make_message(request, user_id):
    user = User.objects.get(pk=user_id)
    if user != request.user:
        raise Http404
    else:
        friend_list = [friend for friend in Friend.objects.friends(request.user)]
        if request.method != 'POST':
            # No data submitted; create a blank form.
            form = MakeMessageForm
            status_message = ''
        else:
            form = MakeMessageForm(data=request.POST)
            status_message = ''
            if form.is_valid():
                new_message = form.save(commit=False)
                new_message.from_user = request.user
                new_message.to_user.is_authenticated()
                if new_message.to_user not in friend_list:
                    status_message = 'That user is not in your friends list.'
                else:
                    new_message.save()
                    status_message += 'Message Sent!'
                    return HttpResponseRedirect(reverse('users:inbox', args=[request.user.pk]))

    context = {'form': form, 'status_message': status_message}
    common_context = get_common_context(request.user)
    for key, value in common_context.items():
        context[key] = value
    return render(request, 'users/make_message.html', context)