from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.safestring import SafeString
from django.template.defaultfilters import truncatechars
import textwrap

"""
Language Model for Phaidra
"""
class Language(models.Model):
    """
    Languages that Phaidra is available in. Used to determine the content 
    that the user sees in the interface and learning material.
    """
    DIRECTION_CHOICES = (
        ('ltr', 'Left-to-right'),
        ('rtl', 'Right-to-left')
    )

    name = models.CharField("language name (english)", 
                            max_length=200, 
                            help_text='(e.g. German)')

    local_name = models.CharField("language name", 
                            max_length=200, 
                            help_text='(e.g. Deutsch)')

    locale = models.CharField("language code", 
                            max_length=5, 
                            help_text='(e.g. de-at)')

    short_code = models.CharField("shortcode", 
                            max_length=5, 
                            help_text='(e.g. \'de\')')

    direction = models.CharField('text direction', 
                            choices=DIRECTION_CHOICES, 
                            max_length=3)

    modern = models.BooleanField('modern', 
                            help_text=textwrap.dedent("""
                                Check this box if this is a modern language.
                            """),
                            default=True)

    def __unicode__(self):
        return unicode(self.name) or u''

"""
Category Model for Phaidra.
"""
class Category(models.Model):
    """
    Grammar topics are divided into different categories. Which category 
    is selected will determine how the the topic is displayed in the 
    lesson list view in the interface.
    """
    # Verbs, Nouns, Adjectives, etc.
    name = models.CharField('category name', 
                            max_length=200)

    # alphabet/lambda.svg
    graphic = models.CharField(max_length=200, 
                            help_text=textwrap.dedent("""
                                Image within /static/images/ that 
                                should be shown on lesson tiles 
                                within this category.
                            """),
                            null=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __unicode__(self):
        return unicode(self.name) or u''

"""
Custom User Model for Phaidra.
"""
class AppUser(AbstractUser):
    """
    User model to which all other information about the user is linked 
    (e.g. the language they speak, the language they're learning, and 
    the submissions they make (submissions are stored in neo4j, see 
    api/submissions.py)
    """
    objects = UserManager()

    lang_learning = models.ForeignKey(Language, 
                            verbose_name='Learning Language', 
                            related_name='learning', 
                            null=True, 
                            help_text='Language the user is learning.')

    lang_speaking = models.ForeignKey(Language, 
                            verbose_name='Speaks Language', 
                            related_name='speaking', 
                            null=True, 
                            help_text='Language the user speaks.') 
    
    def __unicode__(self):
        return unicode(self.username) or u''

"""
Aspect Model for Phaidra.
"""
class Aspect(models.Model):
    """
    Aspect model is used by task to explicitly state what kind of 
    knowledge a user is demonstrating while performing this task. 
    E.g. a "Fill in vocab in context" tests all three aspects.
    """
    ASPECT_CHOICES = (
        ('V', 'Vocabulary'),
        ('S', 'Syntax'),
        ('M', 'Morphology')
    )

    name = models.CharField('aspect name', 
                            choices=ASPECT_CHOICES, 
                            max_length=1, 
                            help_text='')

    def __unicode__(self):
        return unicode(self.get_name_display()) or u''

"""
Task Model for Phaidra
"""
class Task(models.Model):
    """
    A task is essentially a learning exercise. Each task name must 
    correspond to a file in static/js/views/lessons/tasks. Tasks are 
    then organized into sequences via a relation to the TaskSequence 
    model, which in turn is linked to a grammar topic.
    """
    ENDPOINT_CHOICES = (
        ('word', 'word'),
        ('sentence', 'sentence'),
        ('document', 'document')
    )

    name = models.CharField('task name', 
                            max_length=100, 
                            help_text=textwrap.dedent("""
                                Should corespond to something in <a 
                                href="https://github.com/OpenPhilology/
                                phaidra/tree/master/static/js/views/
                                lessons/tasks" target="_blank">
                                this folder on Github</a>.
                            """))

    endpoint = models.CharField('API endpoint', 
                            max_length=20, 
                            choices=ENDPOINT_CHOICES, 
                            help_text=textwrap.dedent("""
                                Defines the API endpoint to which the 
                                morphological query should be appended.
                            """))

    aspect = models.ManyToManyField(Aspect, 
                            verbose_name='knowledge aspect', 
                            help_text=textwrap.dedent("""
                                Which aspect(s) of this user\'s knowledge 
                                is tested?
                            """))

    success_msg = models.CharField('success message', 
                            max_length=200, 
                            help_text=textwrap.dedent("""
                                Message the user sees on success.
                            """),
                            null=True, 
                            blank=True)

    hint_msg = models.CharField('hint message', 
                            max_length=200, 
                            help_text=textwrap.dedent("""
                                Message the user sees on their first 
                                incorrect attempt.
                            """),
                            null=True, 
                            blank=True)

    def __unicode__(self):
        return unicode(self.name) or u''

"""
Task Sequence Model for Phaidra.
"""
class TaskSequence(models.Model):
    """
    A Task Sequence is, well, an ordered list of tasks. Metadata about 
    this relation is contained in the TaskContext model.
    """
    tasks = models.ManyToManyField(Task, 
                            through='TaskContext')

    name = models.CharField('task sequence name', 
                            max_length=200, 
                            help_text=textwrap.dedent("""
                                Name of this unique set and order of tasks. 
                                (e.g. "Beginner Nouns" or "Learn to Read Greek")
                            """))

    def all_tasks(self):
        return SafeString(', '.join([t.name for t in self.tasks.all()])) 

    def __unicode__(self):
        return unicode(self.name) or u''

"""
Task Context Model for Phaidra
"""
class TaskContext(models.Model):
    """
    Describes the relationship of a task to the sequences it is found 
    in. It often helps us decide whether the user should move on from 
    one task to the next in the task sequence.
    """
    task_sequence = models.ForeignKey(TaskSequence, 
                            verbose_name='task sequence', 
                            help_text=textwrap.dedent("""
                                The task sequence to which task, with 
                                this metadata, belongs.
                            """))

    task = models.ForeignKey(Task, 
                            verbose_name='task', 
                            help_text=textwrap.dedent("""
                                Task that belongs in the sequence at 
                                this point.
                            """))

    # 0.5 means we wait for 50% accuracy before proceeding to next task
    target_accuracy = models.FloatField('target accuracy', 
                            help_text=textwrap.dedent("""
                                Decimal between 0 and 1. When a user 
                                reaches this level of accuracy, 
                                they move to the next task.
                            """))

    max_attempts = models.IntegerField('maximum attempts', 
                            help_text=textwrap.dedent("""
                                Maximum number of times user should be 
                                presented with this task before moving 
                                on to the next.
                            """))

    order = models.IntegerField(help_text=textwrap.dedent("""
                                Order of this task in the defined sequence.
                            """))

"""
Grammar Model for Phaidra
"""
class Grammar(models.Model):
    """
    Each instance of the grammar model is, so to speak, a discrete 
    learning unit. They are the basis of the microlessons found 
    in the frontend.
    """
    ref = models.CharField("Reference", 
                            max_length=10, 
                            unique=True, 
                            help_text=textwrap.dedent("""
                                Refers to the section of the grammar 
                                book you're using.
                            """))

    external_link = models.CharField("external url", 
                            max_length=200, 
                            null=True, 
                            blank=True, 
                            help_text=textwrap.dedent("""
                                Link to section in the grammar book 
                                itself.
                            """))

    query = models.CharField("query string", 
                            max_length=200, 
                            null=True, 
                            blank=True, 
                            help_text=textwrap.dedent("""
                                Describe the morphology of words that 
                                fit this grammar topic.
                            """))

    title = models.CharField("title of grammar section", 
                            max_length=200, 
                            help_text=textwrap.dedent("""
                                Short, descriptive title of the grammar
                                concept.
                            """))

    category = models.ForeignKey(Category, 
                            null=True, 
                            blank=True)

    tasks = models.ForeignKey(TaskSequence, 
                            verbose_name='task sequence', 
                            null=True, 
                            blank=True)

    class Meta:
        verbose_name = 'Grammar Topic'
        ordering = ['title']

    def __unicode__(self):
        return unicode(self.title) or u''

"""
Content Model for Phaidra
"""
class Content(models.Model):
    """
    Content refers to small chunks of information that the user is 
    presented with inside a microlesson. Content is related to other 
    content by an asymmetrical relationship, so that the interface can 
    show users helpful related content while they work through a lesson.
    (E.g. 'Introduction to Verbs' relates to 'The Aorist Tense', but we
    would not want to show users information about the Aorist when they 
    are just learning how Verbs work).
    """
    title = models.CharField("title", 
                            max_length=200, 
                            help_text=textwrap.dedent("""
                                Short, descriptive title of what 
                                content is in this section.
                            """))

    grammar_ref = models.OneToOneField(Grammar, 
                            verbose_name="grammar topic", 
                            null=True, 
                            blank=True, 
                            help_text=textwrap.dedent("""
                                The morphology directly described by 
                                this content.
                            """))

    related_content = models.ManyToManyField('self', 
                            related_name='relates_to', 
                            symmetrical=False, 
                            null=True, 
                            blank=True, 
                            help_text=textwrap.dedent("""
                                Content that would help someone answer 
                                questions about this topic.
                            """))

    source_lang = models.ForeignKey(Language, 
                            related_name='content_written_in', 
                            help_text=textwrap.dedent("""
                                Language the content is written in.
                            """))

    target_lang = models.ForeignKey(Language, 
                            related_name='content_written_about', 
                            help_text='Language the content teaches.')

    content = models.TextField("Learning Content", 
                            help_text=textwrap.dedent("""
                                Write this in <a href="https://github.com/
                                OpenPhilology/phaidra/wiki/Phaidra-flavored-
                                Markdown" target="_blank">Phaidra-flavored 
                                Markdown</a>.
                            """))

    @property
    def content_preview(self):
        """
        Used by the admin interface to show a shortened version of the
        marked down content.
        """
        return truncatechars(self.content, 90);

    def all_related_content(self):
        """
        Fetches and joins the titles of all related content. Used by
        the admin interface.
        """
        return SafeString('<br>'.join([t.title for t in self.related_content.all()])) 

    def __unicode__(self):
        return unicode(self.title) or u''


# SIGNALS
def signals_import():
    """
    Make sure signals are imported early.
    """
    from tastypie.models import create_api_key

    models.signals.post_save.connect(create_api_key, sender=AppUser)

signals_import()
