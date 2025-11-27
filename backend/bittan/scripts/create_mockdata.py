#!/usr/bin/env python3

import os, sys

sys.path.append("..")
os.environ["DJANGO_SETTINGS_MODULE"] = "bittan.settings"
import django

django.setup()

from django.contrib.auth.models import User
from bittan.models import (
    TicketType,
    ChapterEvent,
    Payment,
    Ticket,
    Question,
    QuestionOption,
    Answer,
    AnswerSelectedOptions,
)
from bittan.models.payment import PaymentMethod, PaymentStatus
from bittan.models.question import QuestionType
import datetime

User.objects.create_superuser("admin", None, "admin")
User.objects.create_user("staff", None, "staff", is_staff=True)

NOW = datetime.datetime.now()

standardbiljett = TicketType.objects.create(
    price=200, title="Standardbiljett", description="En vanlig biljett."
)
studentbiljett = TicketType.objects.create(
    price=100, title="Studentbiljett", description="En billigare biljett."
)

chapter_event1 = ChapterEvent.objects.create(
    title="Fysikalen Dag 1",
    description="Första dagen av Fysikalen.",
    total_seats=10,
    sales_stop_at=NOW + datetime.timedelta(days=365),
    event_at=NOW + datetime.timedelta(days=365),
)
chapter_event1.ticket_types.add(standardbiljett, studentbiljett)


payment1 = Payment.objects.create(
    expires_at=NOW + datetime.timedelta(hours=1),
    swish_id="Hej",
    status=PaymentStatus.RESERVED,
    email="mail@mail.com",
    sent_email=False,
    payment_method=PaymentMethod.SWISH,
)

ticket1 = Ticket.objects.create(
    external_id="1234",
    time_created=NOW,
    payment=payment1,
    ticket_type=standardbiljett,
    chapter_event=chapter_event1,
)

chapter_event2 = ChapterEvent.objects.create(
    title="Fysikalen Dag 2",
    description="Andra dagen av Fysikalen.",
    total_seats=10,
    sales_stop_at=NOW + datetime.timedelta(days=365),
    event_at=NOW + datetime.timedelta(days=366),
)
chapter_event2.ticket_types.add(standardbiljett, studentbiljett)

q1 = Question.objects.create(
    title="Namn", question_type=QuestionType.RADIO, chapter_event=chapter_event1
)

opt1_1 = QuestionOption.objects.create(price=0, name="Namn", has_text=True, question=q1)

q2 = Question.objects.create(
    title="Speckost",
    question_type=QuestionType.MULTIPLE_CHOICE,
    chapter_event=chapter_event1,
)

opt2_1 = QuestionOption.objects.create(
    price=0, name="Gluten", has_text=False, question=q2
)
opt2_2 = QuestionOption.objects.create(
    price=0, name="Laktos", has_text=False, question=q2
)
opt2_3 = QuestionOption.objects.create(
    price=0, name="Övrigt", has_text=True, question=q2
)

q3 = Question.objects.create(
    title="Kött?", question_type=QuestionType.RADIO, chapter_event=chapter_event1
)
opt3_1 = QuestionOption.objects.create(
    price=0, name="Gött", has_text=False, question=q3
)
opt3_2 = QuestionOption.objects.create(
    price=0, name="Nött", has_text=False, question=q3
)

q4 = Question.objects.create(
    title="Tillägg",
    question_type=QuestionType.MULTIPLE_CHOICE,
    chapter_event=chapter_event1,
)
opt4_1 = QuestionOption.objects.create(
    name="Extra punsch", price=20, has_text=False, question=q4
)
opt4_2 = QuestionOption.objects.create(
    name="Extra nubbe", price=20, has_text=False, question=q4
)

q5 = Question.objects.create(
    title="Jag kommer att bete mig. ",
    question_type=QuestionType.RADIO,
    chapter_event=chapter_event1,
)
opt5_1 = QuestionOption.objects.create(name="Ja", price=0, has_text=False, question=q5)

q6 = Question.objects.create(
    title="Bilder?",
    question_type=QuestionType.MULTIPLE_CHOICE,
    chapter_event=chapter_event1,
)
opt6_1 = QuestionOption.objects.create(name="Ja", price=0, has_text=False, question=q6)

q7 = Question.objects.create(
    title="Årskurs", question_type=QuestionType.RADIO, chapter_event=chapter_event1
)

opt7_1 = QuestionOption.objects.create(
    name="F-24", price=0, has_text=False, question=q7
)
opt7_2 = QuestionOption.objects.create(
    name="F-23", price=0, has_text=False, question=q7
)
opt7_3 = QuestionOption.objects.create(
    name="F-22", price=0, has_text=False, question=q7
)
opt7_4 = QuestionOption.objects.create(
    name="F-21", price=0, has_text=False, question=q7
)
opt7_5 = QuestionOption.objects.create(
    name="Annan: ", price=0, has_text=True, question=q7
)

p1 = Payment.objects.create(
    expires_at=NOW + datetime.timedelta(hours=1),
    swish_id="Hejsan hoppsan fallerallera när julen kommer ska varenda unge vara glad",
    status=PaymentStatus.FORM_SUBMITTED,
    email="test1@testsson.com",
    sent_email=False,
    payment_method=PaymentMethod.SWISH,
)

t1 = Ticket.objects.create(
    time_created=NOW,
    payment=p1,
    ticket_type=standardbiljett,
    chapter_event=chapter_event1,
)

t1ans1 = Answer.objects.create(
    question=q1,
    ticket=t1,
)

t1opt1_1 = AnswerSelectedOptions.objects.create(
    question_option=opt1_1, answer=t1ans1, text="Namn namnsson"
)

t1ans2 = Answer.objects.create(
    question=q2,
    ticket=t1,
)

t1opt2_1 = AnswerSelectedOptions.objects.create(
    question_option=opt2_1,
    answer=t1ans2,
)

t1opt2_2 = AnswerSelectedOptions.objects.create(
    question_option=opt2_2,
    answer=t1ans2,
)

t1opt2_2 = AnswerSelectedOptions.objects.create(
    question_option=opt2_3,
    answer=t1ans2,
    text="Jag är alergisk mot allt",
)

t1ans3 = Answer.objects.create(
    question=q3,
    ticket=t1,
)

t1opt3_1 = AnswerSelectedOptions.objects.create(
    question_option=opt3_1,
    answer=t1ans3,
)

t1ans4 = Answer.objects.create(
    question=q4,
    ticket=t1,
)


t1ans5 = Answer.objects.create(
    question=q5,
    ticket=t1,
)

t1opt5_1 = AnswerSelectedOptions.objects.create(
    question_option=opt5_1,
    answer=t1ans5,
)

t1ans6 = Answer.objects.create(
    question=q6,
    ticket=t1,
)

t1ans7 = Answer.objects.create(
    question=q7,
    ticket=t1,
)

t1opt7_1 = AnswerSelectedOptions.objects.create(
    question_option=opt7_2,
    answer=t1ans7,
)

p2 = Payment.objects.create(
    expires_at=NOW + datetime.timedelta(hours=1),
    swish_id="Hejsan hoppsan fallerallera när julen kommer ska varenda unge vara glad2",
    status=PaymentStatus.FORM_SUBMITTED,
    email="test2@testsson.com",
    sent_email=False,
    payment_method=PaymentMethod.SWISH,
)

t2 = Ticket.objects.create(
    time_created=NOW,
    payment=p2,
    ticket_type=standardbiljett,
    chapter_event=chapter_event1,
)

t2ans1 = Answer.objects.create(
    question=q1,
    ticket=t2,
)

t2opt1_1 = AnswerSelectedOptions.objects.create(
    question_option=opt1_1, answer=t2ans1, text="Namn namnsson 2"
)

t2ans2 = Answer.objects.create(
    question=q2,
    ticket=t2,
)

t2opt2_1 = AnswerSelectedOptions.objects.create(
    question_option=opt2_1,
    answer=t2ans2,
)

t2opt2_2 = AnswerSelectedOptions.objects.create(
    question_option=opt2_2,
    answer=t2ans2,
)

t2opt2_2 = AnswerSelectedOptions.objects.create(
    question_option=opt2_3,
    answer=t2ans2,
    text="Jag är alergisk mot allt",
)

t2ans3 = Answer.objects.create(
    question=q3,
    ticket=t2,
)

t2opt3_1 = AnswerSelectedOptions.objects.create(
    question_option=opt3_1,
    answer=t2ans3,
)

t2ans4 = Answer.objects.create(
    question=q4,
    ticket=t2,
)


t2ans5 = Answer.objects.create(
    question=q5,
    ticket=t2,
)

t2opt5_1 = AnswerSelectedOptions.objects.create(
    question_option=opt5_1,
    answer=t2ans5,
)

t2ans6 = Answer.objects.create(
    question=q6,
    ticket=t2,
)

t2ans7 = Answer.objects.create(
    question=q7,
    ticket=t2,
)

t2opt7_1 = AnswerSelectedOptions.objects.create(
    question_option=opt7_2,
    answer=t2ans7,
)


# I gave up and let ChatGPT generate the rest of the mock data:
#
p3 = Payment.objects.create(
    expires_at=NOW + datetime.timedelta(hours=1),
    swish_id="SWISH-ID-33333",
    status=PaymentStatus.FORM_SUBMITTED,
    email="test3@example.com",
    sent_email=False,
    payment_method=PaymentMethod.SWISH,
)

t3 = Ticket.objects.create(
    time_created=NOW,
    payment=p3,
    ticket_type=standardbiljett,
    chapter_event=chapter_event1,
)

# q1 – Namn
t3ans1 = Answer.objects.create(question=q1, ticket=t3)
AnswerSelectedOptions.objects.create(
    question_option=opt1_1, answer=t3ans1, text="Karl Karlsson"
)

# q2 – Speckost (None selected)
t3ans2 = Answer.objects.create(question=q2, ticket=t3)

# q3 – Meat (Gött)
t3ans3 = Answer.objects.create(question=q3, ticket=t3)
AnswerSelectedOptions.objects.create(question_option=opt3_1, answer=t3ans3)

# q4 – Tillägg (none)
t3ans4 = Answer.objects.create(question=q4, ticket=t3)

# q5 – Ja
t3ans5 = Answer.objects.create(question=q5, ticket=t3)
AnswerSelectedOptions.objects.create(question_option=opt5_1, answer=t3ans5)

# q6 – Bilder? (yes)
t3ans6 = Answer.objects.create(question=q6, ticket=t3)
AnswerSelectedOptions.objects.create(question_option=opt6_1, answer=t3ans6)

# q7 – Årskurs (F-21)
t3ans7 = Answer.objects.create(question=q7, ticket=t3)
AnswerSelectedOptions.objects.create(question_option=opt7_4, answer=t3ans7)


p4 = Payment.objects.create(
    expires_at=NOW + datetime.timedelta(hours=1),
    swish_id="SWISH-ID-44444",
    status=PaymentStatus.FORM_SUBMITTED,
    email="test4@example.com",
    sent_email=False,
    payment_method=PaymentMethod.SWISH,
)

t4 = Ticket.objects.create(
    time_created=NOW,
    payment=p4,
    ticket_type=standardbiljett,
    chapter_event=chapter_event1,
)

# q1 – Namn
t4ans1 = Answer.objects.create(question=q1, ticket=t4)
AnswerSelectedOptions.objects.create(
    question_option=opt1_1, answer=t4ans1, text="Emma Ekström"
)

# q2 – Speckost (Laktos + Övrigt)
t4ans2 = Answer.objects.create(question=q2, ticket=t4)
AnswerSelectedOptions.objects.create(question_option=opt2_2, answer=t4ans2)
AnswerSelectedOptions.objects.create(
    question_option=opt2_3, answer=t4ans2, text="Bara lite känslig"
)

# q3 – Kött (Nött)
t4ans3 = Answer.objects.create(question=q3, ticket=t4)
AnswerSelectedOptions.objects.create(question_option=opt3_2, answer=t4ans3)

# q4 – Tillägg (both punsch + nubbe)
t4ans4 = Answer.objects.create(question=q4, ticket=t4)
AnswerSelectedOptions.objects.create(question_option=opt4_1, answer=t4ans4)
AnswerSelectedOptions.objects.create(question_option=opt4_2, answer=t4ans4)

# q5 – Ja (behave)
t4ans5 = Answer.objects.create(question=q5, ticket=t4)
AnswerSelectedOptions.objects.create(question_option=opt5_1, answer=t4ans5)

# q6 – Bilder (yes)
t4ans6 = Answer.objects.create(question=q6, ticket=t4)
AnswerSelectedOptions.objects.create(question_option=opt6_1, answer=t4ans6)

# q7 – Årskurs (Annan: Med text)
t4ans7 = Answer.objects.create(question=q7, ticket=t4)
AnswerSelectedOptions.objects.create(
    question_option=opt7_5, answer=t4ans7, text="Utbytesstudent"
)


p5 = Payment.objects.create(
    expires_at=NOW + datetime.timedelta(hours=1),
    swish_id="SWISH-ID-55555",
    status=PaymentStatus.FORM_SUBMITTED,
    email="test5@example.com",
    sent_email=False,
    payment_method=PaymentMethod.SWISH,
)

t5 = Ticket.objects.create(
    time_created=NOW,
    payment=p5,
    ticket_type=standardbiljett,
    chapter_event=chapter_event1,
)

# q1 – Namn
t5ans1 = Answer.objects.create(question=q1, ticket=t5)
AnswerSelectedOptions.objects.create(
    question_option=opt1_1, answer=t5ans1, text="Oskar Oskarsson"
)

# q2 – Speckost (Gluten only)
t5ans2 = Answer.objects.create(question=q2, ticket=t5)
AnswerSelectedOptions.objects.create(question_option=opt2_1, answer=t5ans2)

# q3 – Kött? (Gött)
t5ans3 = Answer.objects.create(question=q3, ticket=t5)
AnswerSelectedOptions.objects.create(question_option=opt3_1, answer=t5ans3)

# q4 – Tillägg (none)
t5ans4 = Answer.objects.create(question=q4, ticket=t5)

# q5 – Ja
t5ans5 = Answer.objects.create(question=q5, ticket=t5)
AnswerSelectedOptions.objects.create(question_option=opt5_1, answer=t5ans5)

# q6 – Bilder? (none selected)
t5ans6 = Answer.objects.create(question=q6, ticket=t5)

# q7 – Årskurs (F-22)
t5ans7 = Answer.objects.create(question=q7, ticket=t5)
AnswerSelectedOptions.objects.create(question_option=opt7_3, answer=t5ans7)


p6 = Payment.objects.create(
    expires_at=NOW + datetime.timedelta(hours=1),
    swish_id="SWISH-ID-66666",
    status=PaymentStatus.FORM_SUBMITTED,
    email="test6@example.com",
    sent_email=False,
    payment_method=PaymentMethod.SWISH,
)

t6 = Ticket.objects.create(
    time_created=NOW,
    payment=p6,
    ticket_type=standardbiljett,
    chapter_event=chapter_event1,
)

# q1 – Namn
t6ans1 = Answer.objects.create(question=q1, ticket=t6)
AnswerSelectedOptions.objects.create(
    question_option=opt1_1, answer=t6ans1, text="Sara Svensson"
)

# q2 – Speckost (Laktos + Gluten)
t6ans2 = Answer.objects.create(question=q2, ticket=t6)
AnswerSelectedOptions.objects.create(question_option=opt2_1, answer=t6ans2)
AnswerSelectedOptions.objects.create(question_option=opt2_2, answer=t6ans2)

# q3 – Kött? (Nött)
t6ans3 = Answer.objects.create(question=q3, ticket=t6)
AnswerSelectedOptions.objects.create(question_option=opt3_2, answer=t6ans3)

# q4 – Tillägg (Extra nubbe)
t6ans4 = Answer.objects.create(question=q4, ticket=t6)
AnswerSelectedOptions.objects.create(question_option=opt4_2, answer=t6ans4)

# q5 – Ja
t6ans5 = Answer.objects.create(question=q5, ticket=t6)
AnswerSelectedOptions.objects.create(question_option=opt5_1, answer=t6ans5)

# q6 – Bilder? (yes)
t6ans6 = Answer.objects.create(question=q6, ticket=t6)
AnswerSelectedOptions.objects.create(question_option=opt6_1, answer=t6ans6)

# q7 – Årskurs (F-23)
t6ans7 = Answer.objects.create(question=q7, ticket=t6)
AnswerSelectedOptions.objects.create(question_option=opt7_2, answer=t6ans7)


p7 = Payment.objects.create(
    expires_at=NOW + datetime.timedelta(hours=1),
    swish_id="SWISH-ID-77777",
    status=PaymentStatus.FORM_SUBMITTED,
    email="test7@example.com",
    sent_email=False,
    payment_method=PaymentMethod.SWISH,
)

t7 = Ticket.objects.create(
    time_created=NOW,
    payment=p7,
    ticket_type=standardbiljett,
    chapter_event=chapter_event1,
)

# q1 – Namn
t7ans1 = Answer.objects.create(question=q1, ticket=t7)
AnswerSelectedOptions.objects.create(
    question_option=opt1_1, answer=t7ans1, text="Hanna Håkansson"
)

# q2 – Speckost (only Övrigt)
t7ans2 = Answer.objects.create(question=q2, ticket=t7)
AnswerSelectedOptions.objects.create(
    question_option=opt2_3, answer=t7ans2, text="Alergisk mot citrus"
)

# q3 – Kött? (Gött)
t7ans3 = Answer.objects.create(question=q3, ticket=t7)
AnswerSelectedOptions.objects.create(question_option=opt3_1, answer=t7ans3)

# q4 – Tillägg (both)
t7ans4 = Answer.objects.create(question=q4, ticket=t7)
AnswerSelectedOptions.objects.create(question_option=opt4_1, answer=t7ans4)
AnswerSelectedOptions.objects.create(question_option=opt4_2, answer=t7ans4)

# q5 – Ja
t7ans5 = Answer.objects.create(question=q5, ticket=t7)
AnswerSelectedOptions.objects.create(question_option=opt5_1, answer=t7ans5)

# q6 – Bilder? (yes)
t7ans6 = Answer.objects.create(question=q6, ticket=t7)
AnswerSelectedOptions.objects.create(question_option=opt6_1, answer=t7ans6)

# q7 – Årskurs (Annan: with text)
t7ans7 = Answer.objects.create(question=q7, ticket=t7)
AnswerSelectedOptions.objects.create(
    question_option=opt7_5, answer=t7ans7, text="Masterstudent"
)
