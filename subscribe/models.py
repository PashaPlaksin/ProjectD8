from django.db import models

class SubscribeUser(models.Model):

  email = models.EmailField()


  def __str__(self):
    return self.email

class Appointment(models.Model):

    client_name = models.CharField(
        max_length=200
    )
    message = models.TextField()

    def __str__(self):
        return f'{self.client_name}: {self.message}'