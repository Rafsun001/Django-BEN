from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Chatbot1(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot1")
    title = models.CharField(max_length=200)
    timestamp_parent = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title}" 
    
class ChatHistory1(models.Model):
    chat = models.ForeignKey(Chatbot1, on_delete=models.CASCADE, related_name="ChatHistory1")
    role = models.CharField(max_length=5)
    message = models.CharField(max_length=2000000)
    timestamp_child = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp_child']  

    def __str__(self):
        return f"{self.chat}" 

    
class Chatbot2(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot2")
    title = models.CharField(max_length=200)
    timestamp_parent = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title}" 
    

class ChatHistory2(models.Model):
    chat = models.ForeignKey(Chatbot2, on_delete=models.CASCADE, related_name="ChatHistory2")
    role = models.CharField(max_length=5)
    message = models.CharField(max_length=2000000)
    timestamp_child = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp_child']  

    def __str__(self):
        return f"{self.chat}" 
    

class Chatbot3(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot3")
    title = models.CharField(max_length=200)
    timestamp_parent = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title}" 


class ChatHistory3(models.Model):
    chat = models.ForeignKey(Chatbot3, on_delete=models.CASCADE, related_name="ChatHistory3")
    role = models.CharField(max_length=5)
    message = models.CharField(max_length=2000000)
    timestamp_child = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp_child']  

    def __str__(self):
        return f"{self.chat}" 
    

class Chatbot4(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot4")
    title = models.CharField(max_length=200)
    timestamp_parent = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title}" 
    

class ChatHistory4(models.Model):
    chat = models.ForeignKey(Chatbot4, on_delete=models.CASCADE, related_name="ChatHistory4")
    role = models.CharField(max_length=5)
    message = models.CharField(max_length=2000000)
    timestamp_child = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp_child']  

    def __str__(self):
        return f"{self.chat}" 
    
class Chatbot5(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot5")
    title = models.CharField(max_length=200)
    timestamp_parent = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}" 

class ChatHistory5(models.Model):
    chat = models.ForeignKey(Chatbot5, on_delete=models.CASCADE, related_name="ChatHistory5")
    role = models.CharField(max_length=5)
    message = models.CharField(max_length=2000000)
    timestamp_child = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp_child']  

    def __str__(self):
        return f"{self.chat}" 

class Chatbot6(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot6")
    title = models.CharField(max_length=200)
    timestamp_parent = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}" 
    
class ChatHistory6(models.Model):
    chat = models.ForeignKey(Chatbot6, on_delete=models.CASCADE, related_name="ChatHistory6")
    role = models.CharField(max_length=5)
    message = models.CharField(max_length=2000000)
    timestamp_child = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp_child']  

    def __str__(self):
        return f"{self.chat}" 


class Chatbot7(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot7")
    title = models.CharField(max_length=200)
    timestamp_parent = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}" 
    
class ChatHistory7(models.Model):
    chat = models.ForeignKey(Chatbot7, on_delete=models.CASCADE, related_name="ChatHistory7")
    role = models.CharField(max_length=5)
    message = models.CharField(max_length=2000000)
    timestamp_child = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp_child']  

    def __str__(self):
        return f"{self.chat}" 
    
class Chatbot8(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot8")
    title = models.CharField(max_length=200)
    timestamp_parent = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}" 
    
class ChatHistory8(models.Model):
    chat = models.ForeignKey(Chatbot8, on_delete=models.CASCADE, related_name="ChatHistory8")
    role = models.CharField(max_length=5)
    message = models.CharField(max_length=2000000)
    timestamp_child = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp_child']  

    def __str__(self):
        return f"{self.chat}" 
    

class Chatbot9(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot9")
    title = models.CharField(max_length=200)
    timestamp_parent = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title}" 
    
class ChatHistory9(models.Model):
    chat = models.ForeignKey(Chatbot9, on_delete=models.CASCADE, related_name="ChatHistory9")
    role = models.CharField(max_length=5)
    message = models.CharField(max_length=2000000)
    timestamp_child = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp_child']  

    def __str__(self):
        return f"{self.chat}" 
    

class Chatbot10(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot10")
    title = models.CharField(max_length=200)
    timestamp_parent = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}" 
    

class ChatHistory10(models.Model):
    chat = models.ForeignKey(Chatbot10, on_delete=models.CASCADE, related_name="ChatHistory10")
    role = models.CharField(max_length=5)
    message = models.CharField(max_length=2000000)
    timestamp_child = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp_child']  

    def __str__(self):
        return f"{self.chat}" 


class Chatbot11(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot11")
    title = models.CharField(max_length=200)
    timestamp_parent = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}" 
    

class ChatHistory11(models.Model):
    chat = models.ForeignKey(Chatbot11, on_delete=models.CASCADE, related_name="ChatHistory11")
    role = models.CharField(max_length=5)
    message = models.CharField(max_length=2000000)
    timestamp_child = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp_child']  

    def __str__(self):
        return f"{self.chat}" 
    


class Chatbot12(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chatbot14")
    title = models.CharField(max_length=200)
    timestamp_parent = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}" 
    

class ChatHistory12(models.Model):
    chat = models.ForeignKey(Chatbot12, on_delete=models.CASCADE, related_name="ChatHistory14")
    role = models.CharField(max_length=5)
    message = models.CharField(max_length=2000000)
    timestamp_child = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp_child']  

    def __str__(self):
        return f"{self.chat}" 
    
