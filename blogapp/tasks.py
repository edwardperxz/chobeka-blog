from celery import shared_task
import csv
import os
from django.conf import settings
from django.contrib.auth.models import User
from .models import Blog, Review, Comment
import logging

@shared_task
def export_all_data_to_csv():
    """
    Exports all Users, Blogs, Reviews, and Comments to a CSV file.
    Returns the path to the exported file or an error message.
    """
    logger = logging.getLogger(__name__)
    base_path = settings.BASE_DIR

    try:
        # Export Users
        users_path = os.path.join(base_path, 'usuarios_exportados.csv')
        with open(users_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Username', 'Email', 'Password'])
            for user in User.objects.iterator():
                writer.writerow([user.username, user.email, user.password])

        # Export Blogs
        blogs_path = os.path.join(base_path, 'blogs_exportados.csv')
        with open(blogs_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Title', 'Author', 'Created At'])
            for blog in Blog.objects.select_related('author').iterator():
                writer.writerow([blog.title, blog.author.username, blog.created_at])

        # Export Reviews
        reviews_path = os.path.join(base_path, 'reviews_exportados.csv')
        with open(reviews_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Blog Title', 'Reviewer', 'Rating', 'Comment'])
            for review in Review.objects.select_related('blog', 'reviewer').iterator():
                writer.writerow([
                    review.blog.title if review.blog else '',
                    review.reviewer.username if review.reviewer else '',
                    review.rating,
                    review.comment
                ])

        # Export Comments
        comments_path = os.path.join(base_path, 'comentarios_exportados.csv')
        with open(comments_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Blog Title', 'Reviewer', 'Commenter', 'Content'])
            for comment in Comment.objects.select_related('review__blog', 'review__reviewer', 'commenter').iterator():
                writer.writerow([
                    comment.review.blog.title if comment.review and comment.review.blog else '',
                    comment.review.reviewer.username if comment.review and comment.review.reviewer else '',
                    comment.commenter.username if comment.commenter else '',
                    comment.content
                ])

        logger.info("Datos exportados correctamente a archivos separados.")
        return {
            'users': users_path,
            'blogs': blogs_path,
            'reviews': reviews_path,
            'comments': comments_path
        }
    except Exception as e:
        logger.exception("Error al exportar datos a CSV")
        return f"Error: {str(e)}"