from django.db import models

# Create your models here.
class actbook(models.Model):
    act_name = models.CharField(max_length=255, unique=True)
    act_description = models.TextField(blank=True, null=True)
    act_date_enacted = models.DateField(null=True, blank=True)
    act_short_name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    act_name_hindi = models.CharField(max_length=255, blank=True, null=True)
    act_pdf = models.FileField(upload_to='act_pdfs/', blank=True, null=True)
    act_image = models.ImageField(upload_to='act_images/', blank=True, null=True)
    act_pdf_hindi = models.FileField(upload_to='act_pdfs_hindi/', blank=True, null=True)
    act_image_hindi = models.ImageField(upload_to='act_images_hindi/', blank=True, null=True)

    def __str__(self):
        return self.act_name

    class Meta:
        verbose_name = "Act Book"
        verbose_name_plural = "Act Books"
        ordering = ['act_name']

class actbookchapter(models.Model):
    act = models.ForeignKey(actbook, related_name='chapters', on_delete=models.CASCADE)
    chapter_number = models.PositiveIntegerField()
    chapter_title = models.CharField(max_length=255)
    chapter_title_hindi = models.CharField(max_length=255, blank=True, null=True)
    chapter_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.act.act_short_name} - Chapter {self.chapter_number}: {self.chapter_title}"

    class Meta:
        verbose_name = "Act Book Chapter"
        verbose_name_plural = "Act Book Chapters"
        ordering = ['act', 'chapter_number']
        unique_together = ('act', 'chapter_number')

class actbooksection(models.Model):
    chapter = models.ForeignKey(actbookchapter, related_name='sections', on_delete=models.CASCADE)
    section_number = models.CharField(max_length=50)
    section_title = models.CharField(max_length=255)
    section_title_hindi = models.CharField(max_length=255, blank=True, null=True)
    section_text = models.TextField(blank=True, null=True)
    section_text_hindi = models.TextField(blank=True, null=True)
    old_section_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.chapter.act.act_name} - Chapter {self.chapter.chapter_number} - Section {self.section_number}: {self.section_title}"

    class Meta:
        verbose_name = "Act Book Section"
        verbose_name_plural = "Act Book Sections"
        ordering = ['chapter', 'section_number']
        unique_together = ('chapter', 'section_number')

class similarsection(models.Model):
    section = models.ForeignKey(actbooksection, related_name='similar_sections', on_delete=models.CASCADE)
    similar_section = models.ForeignKey(actbooksection, related_name='similar_to_sections', on_delete=models.CASCADE)

    def __str__(self):
        return f"Similar Section: {self.section} - {self.similar_section}"

    class Meta:
        verbose_name = "Similar Section"
        verbose_name_plural = "Similar Sections"
        unique_together = ('section', 'similar_section')
