from website.worker import celery
from website.models import *
from datetime import datetime
from celery.schedules import crontab
from website.mail_sent import send_email,main
from jinja2 import Template

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    print("Inside scheduler")
    
    
    # Monthly report send to via mail in evenry 10 second.
    # sender.add_periodic_task(10.0, monthly_report_by_email.s() )
    
    
    # Monthly report send to via mail  in one day of 1 week at 7:30 
    sender.add_periodic_task(crontab(hour=7, minute=30, day_of_week=1), monthly_report_by_email.s() )
    
    
    # Daily Reminder send via mail in every second.
    # sender.add_periodic_task(10.0, daily_reminder_by_email.s())
    
    
    # Daily Reminder send in the evenry day at mid night.
    sender.add_periodic_task(crontab(hour=0, minute=0), daily_reminder_by_email.s())

    


@celery.task()
def print_current_time():
    print("start")
    now = datetime.now()
    print("now in task ", now)
    dtstr = now.strftime("%d/%m/%Y %H:%M:%S")
    # print("inside Task")
    # print("hello "+ name )
    print("complete")
    return dtstr
    


# Daily Reminder mail setup.
@celery.task()
def daily_reminder_by_email():
    
    
    # Fetch all user form the database.
    all_user = User.query.all()
    
    # Iterate all user.
    for user in all_user:
        
        # Check the date of the login user.
        if user.activeTime < datetime.now().date():
            
            # Now Open the Mail.html file.
            with open("mail.html", 'r') as h:
                temp=Template(h.read())
                # send_email(user.email, subject="Daily Reminder",message="Hi" + user.first_name)
                send_email(user.email, subject="Daily Reminder",message=temp.render(name=user),)


    return "Successfull Sending the Daily Reminder"
    


@celery.task()
def monthly_report_by_email():
    # Fetch all users from the database
    users = User.query.all()

    # Create report
    for user in users:
        # Retrieve playlists created by the user
        user_playlists = Playlist.query.filter_by(user_id=user.id).all()

        # Retrieve albums created by the user
        user_albums = Album.query.filter_by(user_id=user.id).all()

        # Retrieve songs uploaded by the user
        user_songs_count = len(user.songs)

        # Generate report message
        message = f"Dear {user.email},\n\nHere is your monthly report:\n\n"
        message += f"Playlists created: {[playlist.name for playlist in user_playlists]}\n"
        message += f"Albums created: {[album.name for album in user_albums]}\n"
        message += f"Songs uploaded: {user_songs_count}\n\n"
        message += "Best regards,\nYour Music App Team"
        
        with open("monthly.html", 'r') as h:
            temp=Template(h.read())
        # Send email
            send_email(user.email, subject="Monthly Report", message=temp.render(
            user_email=user.email,
            playlists_created=[playlist.name for playlist in user_playlists],
            albums_created=[album.name for album in user_albums],
            songs_uploaded=user_songs_count
        ))

    # Print confirmation
    print(f"Monthly reports sent at: {datetime.now()}")
    
    return "Successfully Sennding the Monthly Report"
