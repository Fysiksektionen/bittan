#!/usr/bin/env python3

import os, sys

sys.path.append("..")
os.environ['DJANGO_SETTINGS_MODULE'] = "bittan.settings"
import django
django.setup()

from django.contrib.auth.models import User
from bittan.models import TicketType, ChapterEvent, Payment, Ticket, Question, QuestionOption, Answer, AnswerSelectedOptions
from bittan.models.payment import PaymentMethod, PaymentStatus
from bittan.models.question import QuestionType
from bittan.models.question_option import FieldOptions
import datetime

User.objects.create_superuser("admin", None, "admin")
User.objects.create_user("staff", None, "staff", is_staff=True)

NOW = datetime.datetime.now()

standardbiljett = TicketType.objects.create(price=200, title="Standardbiljett", description="En vanlig biljett.")
studentbiljett = TicketType.objects.create(price=100, title="Studentbiljett", description="En billigare biljett.")

chapter_event1 = ChapterEvent.objects.create(title="Fysikalen Dag 1", description="Första dagen av Fysikalen.", total_seats=10, sales_stop_at=NOW+datetime.timedelta(days=365), event_at=NOW+datetime.timedelta(days=365))
chapter_event1.ticket_types.add(standardbiljett, studentbiljett)


payment1 = Payment.objects.create(
            expires_at = NOW + datetime.timedelta(hours=1),
            swish_id = "Hej",
            status = PaymentStatus.RESERVED,
            email = "mail@mail.com",
            sent_email = False,
            payment_method = PaymentMethod.SWISH,
        )

ticket1 = Ticket.objects.create(
            external_id = "1234",
            time_created = NOW,
            payment = payment1,
            ticket_type = standardbiljett,
            chapter_event = chapter_event1
        )

chapter_event2 = ChapterEvent.objects.create(title="Fysikalen Dag 2", description="Andra dagen av Fysikalen.", total_seats=10, sales_stop_at=NOW+datetime.timedelta(days=365), event_at=NOW+datetime.timedelta(days=366))
chapter_event2.ticket_types.add(standardbiljett, studentbiljett)

q1 = Question.objects.create(
                title = "Namn", 
                question_type = QuestionType.RADIO,
                chapter_event = chapter_event1
        )

opt1_1 = QuestionOption.objects.create(
                price = 0,
                name = "Namn",
                text = FieldOptions.MANDATORY,
                question = q1
        )

q2 = Question.objects.create(
                title = "Speckost", 
                question_type = QuestionType.MULTIPLE_CHOICE,
                chapter_event = chapter_event1
        )

opt2_1 = QuestionOption.objects.create(
                price = 0,
                name = "Gluten",
                text = FieldOptions.NO_TEXT,
                question = q2
        )
opt2_2 = QuestionOption.objects.create(
                price = 0,
                name = "Laktos",
                text = FieldOptions.NO_TEXT,
                question = q2
        )
opt2_3 = QuestionOption.objects.create(
                price = 0,
                name = "Övrigt",
                text = FieldOptions.MANDATORY,
                question = q2
        )

q3 = Question.objects.create(
                title = "Kött?", 
                question_type = QuestionType.RADIO,
                chapter_event = chapter_event1
        )
opt3_1 = QuestionOption.objects.create(
                price = 0,
                name = "Gött",
                text = FieldOptions.NO_TEXT,
                question = q3
        )
opt3_2 = QuestionOption.objects.create(
                price = 0,
                name = "Nött",
                text = FieldOptions.NO_TEXT,
                question = q3
        )

q4 = Question.objects.create(
                title = "Tillägg", 
                question_type = QuestionType.MULTIPLE_CHOICE,
                chapter_event = chapter_event1
        )
opt4_1 = QuestionOption.objects.create(
                name = "Extra punsch",
                price = 20,
                text = FieldOptions.NO_TEXT,
                question = q4
        )
opt4_2 = QuestionOption.objects.create(
                name = "Extra nubbe",
                price = 20,
                text = FieldOptions.NO_TEXT,
                question = q4
        )

q5 = Question.objects.create(
                title = "Jag kommer att bete mig. ", 
                question_type = QuestionType.RADIO,
                chapter_event = chapter_event1
        )
opt5_1 = QuestionOption.objects.create(
                name = "Ja",
                price = 0,
                text = FieldOptions.NO_TEXT,
                question = q5
        )

q6 = Question.objects.create(
                title = "Bilder?", 
                question_type = QuestionType.MULTIPLE_CHOICE,
                chapter_event = chapter_event1
        )
opt6_1 = QuestionOption.objects.create(
                name = "Ja",
                price = 0,
                text = FieldOptions.NO_TEXT,
                question = q6
        )

q7 = Question.objects.create(
                title = "Årskurs", 
                question_type = QuestionType.RADIO,
                chapter_event = chapter_event1
        )

opt7_1 = QuestionOption.objects.create(
                name = "F-24",
                price = 0,
                text = FieldOptions.NO_TEXT,
                question = q7
        )
opt7_2 = QuestionOption.objects.create(
                name = "F-23",
                price = 0,
                text = FieldOptions.NO_TEXT,
                question = q7
        )
opt7_3 = QuestionOption.objects.create(
                name = "F-22",
                price = 0,
                text = FieldOptions.NO_TEXT,
                question = q7
        )
opt7_4 = QuestionOption.objects.create(
                name = "F-21",
                price = 0,
                text = FieldOptions.NO_TEXT,
                question = q7
        )
opt7_5 = QuestionOption.objects.create(
                name = "Annan: ",
                price = 0,
                text = FieldOptions.MANDATORY,
                question = q7
        )
