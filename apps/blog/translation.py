from modeltranslation.translator import translator, TranslationOptions
from .models import BlogPost, Tag


class BlogPostTranslationOptions(TranslationOptions):
    fields = ('title', 'excerpt', 'content', 'meta_description', 'meta_keywords')


class TagTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


translator.register(BlogPost, BlogPostTranslationOptions)
translator.register(Tag, TagTranslationOptions)
