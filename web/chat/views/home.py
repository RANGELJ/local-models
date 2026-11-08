# web/chat/views/home.py   (or views.py, wherever your home view lives)
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from ..shared.chat_call import chat_call

# from ..models import Conversation, Message


@login_required
def home(request):
    if request.method == "POST":
        from ..tools import DirListing

        content = request.POST.get("content", "").strip()
        # chat_call(content)
        print(DirListing().get_definition())
        return redirect("home")

    chat_messages = []

    return render(request, "chat/home.html", {"chat_messages": chat_messages})
