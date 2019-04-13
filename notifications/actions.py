from . import query_factory
import datetime
from models import Notification
from timelines_and_trends import actions
from direct_messages import actions as action


def get_notifications(notified_username, last_notification_retrieved_id=None):
    """
        This function get list of notifications for a given username by converting lists of dictionaries
        into lists of notification model, it call fucntion from query factory that returns lists of
        dictionaries fit notification model with the given pagination.


        *Parameter:*

            - *username*: user who will be notified .
            - *last_notification_retrieved_id*: id of last notification retrieved

        *Returns*:

            - *models.Notification object*
        """
    if last_notification_retrieved_id is not None:
        try:
            last_notification_retrieved_id = int(last_notification_retrieved_id)
        except ValueError:
            raise
    notifications = query_factory.get_notifications(notified_username)
    try:
        notifications = actions.paginate(dictionaries_list=notifications, required_size=20,
                                         start_after_key='id', start_after_value=last_notification_retrieved_id)
    except TypeError:
        raise
    if notifications is None:
        return None
    notification_list = []
    if len(notifications) == 0:
        return notification_list
    for notification in notifications:
        notification['created_at'] = action.change_time(notification['created_at'])
        notification_list.append(Notification(notification))
    return notification_list


def create_notifications(involved_username, notified_username, type_notification, kweek_id=None):
    """
     This function create a notification in the database.


     *Parameter:*

         - *involved_username*: user who is responsible for the notification.
         - *type_notification*: type of the notification [FOLLOW-REKWEEK-LIKE].
         - *kweek_id*: the id of the kweek involved.

     *Returns:*

         - *None*: If the query was executed successfully.
         - *Exception* object: If the query produced an error.
     """
    if kweek_id is not None and is_kweek(kweek_id) is False:
        raise Exception('A kweek with this username does not exist')
    if actions.is_user(involved_username) is False:
        raise Exception('Involved_username does not exist')
    if actions.is_user(notified_username) is False:
        raise Exception('Notified_username does not exist')
    if type_notification == 'REPLY' or type_notification == 'MENTION':
        return query_factory.create_notifications(involved_username, notified_username, type_notification,
                                                  kweek_id, datetime.datetime.now(), True)
    if type_notification != 'FOLLOW' and type_notification != 'REKWEEK' and type_notification != 'LIKE':
        raise Exception('Type does not exist')
    if is_notification(involved_username, notified_username, type_notification, kweek_id) is True:
        return "already exists"
    return query_factory.create_notifications(involved_username, notified_username, type_notification,
                                              kweek_id, datetime.datetime.now(), False)


# function for testing
def count_notification():
    """
        This function count all notifications in database.


        *Parameter:*

            - no parameter.

        *Returns:*
            - number of notifications in the database.
    """
    return query_factory.count_notification()[0]['count']


def is_kweek(kweek_id):
    """
                This function checks if the kweek_id is in the database or not.


                *Parameter:*

                    - *kweek_id:* kweek_id to be checked in the database.

                *Returns:*
                    - a boolean representing if exists in the database or not.
    """
    if not query_factory.is_kweek(kweek_id):
        return False
    else:
        return True


def is_notification(involved_username, notified_username, type_notification, kweek_id=None):
    result = query_factory.is_notification(involved_username, notified_username, type_notification, kweek_id)
    if not result:
        return False  # if it doesn't exist in database
    else:   # if it exists in database
        if (datetime.timedelta(days=1)+result[0]['created_at']) <= datetime.datetime.today():
            return False  # if expired
        else:
            return True  # if not expired
