from modeltranslation.translator import translator, TranslationOptions
from .models import Project, Technology


class ProjectTranslationOptions(TranslationOptions):
    fields = ('title', 'tagline', 'description')


class TechnologyTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Project, ProjectTranslationOptions)
translator.register(Technology, TechnologyTranslationOptions)
