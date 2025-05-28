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
    export_path = os.path.join(settings.BASE_DIR, 'all_data_export.csv')

    try:
        with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Export Users
            writer.writerow(['Users'])
            writer.writerow(['Username', 'Email'])
            for user in User.objects.iterator():
                writer.writerow([user.username, user.email])
            writer.writerow([])

            # Export Blogs
            writer.writerow(['Blogs'])
            writer.writerow(['Title', 'Author'])
            for blog in Blog.objects.select_related('author').iterator():
                writer.writerow([blog.title, blog.author.username])
            writer.writerow([])

            # Export Reviews
            writer.writerow(['Reviews'])
            writer.writerow(['Blog Title', 'Reviewer', 'Rating', 'Comment'])
            for review in Review.objects.select_related('blog', 'reviewer').iterator():
                writer.writerow([review.blog.title, review.reviewer.username, review.rating, review.comment])
            writer.writerow([])

            # Export Comments
            writer.writerow(['Comments'])
            writer.writerow(['Blog Title', 'Reviewer', 'Commenter', 'Content'])
            for comment in Comment.objects.select_related('review__blog', 'review__reviewer', 'commenter').iterator():
                writer.writerow([
                    comment.review.blog.title,
                    comment.review.reviewer.username,
                    comment.commenter.username,
                    comment.content
                ])
        logger.info(f"Data exported successfully to {export_path}")
        return export_path
    except Exception as e:
        logger.exception("Failed to export data to CSV")
        return f"Error: {str(e)}"