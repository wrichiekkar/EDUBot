# built in
import json
import os
import string
import jsonpickle
import yaml

from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist

try:    
    with open("/Users/hamzamohiuddin/RUHack2021/views/credentials.yaml", 'r') as f:
        credentials = yaml.safe_load(f)
        API_URL = credentials["API_URL"]
        API_KEY = credentials["API_KEY"]
        USER_ID = credentials["USER_ID"]
except OSError as e:
    print(e)
    print("Please enter credentials in the yaml file.")

# Directory in which to download course information
DL_LOCATION = "./output"
DATE_TEMPLATE = "%B %d, %Y %I:%M %p"


class ModuleItemView:
    title = ""
    content_type = ""


class ModuleView:
    name = ""
    items = []

    def __init__(self):
        self.items = []


class DiscussionView:
    title = ""
    posted_date = ""
    body = ""


class SubmissionView:
    grade = ""

    def __init__(self):
        self.grade = ""


class AssignmentView:
    title = ""
    description = ""
    assigned_date = ""
    due_date = ""
    submission = None

    def __init__(self):
        self.submission = SubmissionView()


class CourseView:
    term = ""
    course_code = ""
    name = ""
    assignments = []
    announcements = []
    discussions = []

    def __init__(self):
        self.assignments = []
        self.announcements = []
        self.discussions = []


def make_valid_filename(input_str):
    # Remove invalid characters
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    input_str = "".join(c for c in input_str if c in valid_chars)

    # Remove leading and trailing whitespace
    input_str = input_str.lstrip().rstrip()

    return input_str


def find_course_modules(course, course_view):
    modules_dir = os.path.join(DL_LOCATION, course_view.term,
                               course_view.course_code, "modules")

    # Create modules directory if not present
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)

    module_views = []

    try:
        modules = course.get_modules()

        for module in modules:
            module_view = ModuleView()

            # Name
            module_view.name = str(module.name) if hasattr(module, "name") else ""

            try:
                # Get module items
                module_items = module.get_module_items()

                for module_item in module_items:
                    module_item_view = ModuleItemView()

                    # Title
                    module_item_view.title = str(module_item.title) if hasattr(module_item, "title") else ""

                    # Type
                    module_item_view.content_type = str(module_item.type) if hasattr(module_item, "type") else ""

                    if module_item_view.content_type == "File":
                        module_dir = modules_dir + "/" + make_valid_filename(str(module.name))

                        try:
                            # Create directory for current module if not present
                            if not os.path.exists(module_dir):
                                os.makedirs(module_dir)

                            # Get the file object
                            module_file = course.get_file(str(module_item.content_id))

                            # Create path for module file download
                            module_file_path = module_dir + "/" + make_valid_filename(str(module_file.display_name))

                            # Download file if it doesn't already exist
                            if not os.path.exists(module_file_path):
                                module_file.download(module_file_path)
                        except Exception as e:
                            print("Skipping module file download that gave the following error:")
                            print(e)

                    module_view.items.append(module_item_view)
            except Exception as e:
                print("Skipping module item that gave the following error:")
                print(e)

            module_views.append(module_view)

    except Exception as e:
        print("Skipping entire module that gave the following error:")
        print(e)

    return module_views


def find_course_assignments(course):
    assignment_views = []

    # Get all assignments
    assignments = course.get_assignments()

    try:
        for assignment in assignments:
            # Create a new assignment view
            assignment_view = AssignmentView()

            # Title
            if hasattr(assignment, "name"):
                assignment_view.title = str(assignment.name)
            else:
                assignment_view.title = ""
            # Description
            if hasattr(assignment, "description"):
                assignment_view.description = str(assignment.description)
            else:
                assignment_view.description = ""
            # Assigned date
            if hasattr(assignment, "created_at_date"):
                assignment_view.assigned_date = assignment.created_at_date.strftime(DATE_TEMPLATE)
            else:
                assignment_view.assigned_date = ""
            # Due date
            if hasattr(assignment, "due_at_date"):
                assignment_view.due_date = assignment.due_at_date.strftime(DATE_TEMPLATE)
            else:
                assignment_view.due_date = ""

            # Get my user's submission object
            try:
                submission = assignment.get_submission(USER_ID)

                # Create a new submission view
                assignment_view.submission = SubmissionView()

                # My grade
                assignment_view.submission.grade = str(submission.grade) if hasattr(submission, "grade") else ""

            except ResourceDoesNotExist:
                print('No submission for user: {}'.format(USER_ID))

            assignment_views.append(assignment_view)

    except Exception as e:
        print("Skipping course assignments that gave the following error:")
        print(e)

    return assignment_views


def find_course_announcements(course):
    announcement_views = []

    try:
        announcements = course.get_discussion_topics(only_announcements=True)

        for announcement in announcements:
            discussion_view = get_discussion_view(announcement)

            announcement_views.append(discussion_view)
    except Exception as e:
        print("Skipping announcement that gave the following error:")
        print(e)

    return announcement_views


def get_discussion_view(discussion_topic):
    # Create discussion view
    discussion_view = DiscussionView()

    # Title
    discussion_view.title = str(discussion_topic.title) if hasattr(discussion_topic, "title") else ""
    # Posted date
    discussion_view.posted_date = discussion_topic.created_at_date.strftime("%B %d, %Y %I:%M %p") \
        if hasattr(discussion_topic, "created_at_date") else ""
    # Body
    discussion_view.body = str(discussion_topic.message) if hasattr(discussion_topic, "message") else ""

    return discussion_view


def find_course_discussions(course):
    discussion_views = []

    try:
        discussion_topics = course.get_discussion_topics()

        for discussion_topic in discussion_topics:
            discussion_view = get_discussion_view(discussion_topic)

            discussion_views.append(discussion_view)
    except Exception as e:
        print("Skipping discussion that gave the following error:")
        print(e)

    return discussion_views


def get_course_view(course):
    course_view = CourseView()

    # Course term
    course_view.term = course.term["name"] if hasattr(course, "term") and "name" in course.term.keys() else ""

    # Course code
    course_view.course_code = course.course_code if hasattr(course, "course_code") else ""

    # Course name
    course_view.name = course.name if hasattr(course, "name") else ""

    print("Working on " + course_view.term + ": " + course_view.name)

    # Course assignments
    print("  Getting assignments")
    course_view.assignments = find_course_assignments(course)

    # Course announcements
    print("  Getting announcements")
    course_view.announcements = find_course_announcements(course)

    # Course discussions
    print("  Getting discussions")
    course_view.discussions = find_course_discussions(course)

    return course_view


def export_all_course_data(course_view):
    json_str = json.dumps(json.loads(jsonpickle.encode(course_view, unpicklable=False)), indent=4)

    course_output_dir = os.path.join(DL_LOCATION, course_view.term, course_view.course_code)

    # Create directory if not present
    if not os.path.exists(course_output_dir):
        os.makedirs(course_output_dir)

    course_output_path = os.path.join(course_output_dir, course_view.course_code + ".json")

    with open(course_output_path, "w") as out_file:
        out_file.write(json_str)


def run_export():
    print("Welcome to the Canvas Student Data Export Tool\n")

    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_KEY)

    print("Creating output directory: " + DL_LOCATION + "\n")
    # Create directory if not present
    if not os.path.exists(DL_LOCATION):
        os.makedirs(DL_LOCATION)

    all_courses_views = []

    print("Getting list of all courses\n")
    courses = canvas.get_courses(include="term")

    for course in courses:

        course_view = get_course_view(course)

        all_courses_views.append(course_view)

        print("  Getting modules and downloading module files")
        course_view.modules = find_course_modules(course, course_view)

        print("  Exporting all course data")
        export_all_course_data(course_view)

    print("Exporting data from all courses combined as one file: "
          "all_output.json")

    json_str = json.dumps(json.loads(jsonpickle.encode(all_courses_views, unpicklable=False)), indent=4)

    all_output_path = os.path.join(DL_LOCATION, "all_output.json")

    with open(all_output_path, "w") as out_file:
        out_file.write(json_str)

    print("\nProcess complete. All canvas data exported!")

#if __name__ == '__main__':
#   run_export()