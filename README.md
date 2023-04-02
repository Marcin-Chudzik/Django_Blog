# Blog App

This app is a simple example of a personal Blog, built in Python/Django.

A personal blog application where we can add and delete posts. Tag them with created tags or create a completely new tag. Each post has the ability to add and delete comments. We can search for posts by their titles or content, and filter them by tags. The app displays similar posts under the one that is currently being read, and the homepage displays the currently newest posts and those with the most comments.

Main functionalities in the project:
- adding / removing posts
- tagging posts
- creating new tags
- commenting on posts
- search for a posts
- filtering posts by tags
- displaying similar posts for the reader.
- list of the mostly commented posts
- list of the newest posts.

## How to run

1. Using a GIT write the command.
    ``` bash
    git clone https://github.com/Marcin-Chudzik/django-blog.git
    ```

2. Install PostgreSQL.<br>
**!IMPORTANT!**<br> Default setting for project are wrote to work with PostgreSQL installed with the instruction from below.
If you change the admin username or password, please remember that they need to be changed later in the **django-blog/myblog/settings.py**.
<br><br>*Make a steps till **12** it's enough to run the project.*<br>
Link to the instruction how to install it correctly -> 
<a href="https://www.postgresql.r2schools.com/how-to-install-postgresql-11-and-pgadmin-on-windows-11/">
Installation instruction for PostgreSQL
</a><br>&nbsp;

3. Create a new virtual environment.<br>
Open a repository in the code editor (I'm using Pycharm).<br>
Open a terminal and being in the "django-blog" directory type a command:
    ``` python
    python.exe -m venv venv
    ```

4. Activate a new venv, change directory on "myblog" and use command.
    ``` python
    pip install -r requirements.txt
    ```

5. Create a new text file ".env" in "myblog" directory and write there.<br>(value of a SECRET_KEY can be a whatever else)
    ``` text
    SECRET_KEY=saduoanwodmawdmwioaiome2iomd2m1
    ```
6. Make a migrations and apply them into database, by typing followed commands into the terminal:
    ``` python
    python.exe .\manage.py makemigrations
    ```
    then
    ``` python
    python.exe .\manage.py migrate
    ```
   
7. Create a new superuser. Type command and follow the displayed instructions:
    ``` python
    python.exe .\manage.py createsuperuser
    ```
   
8. I prepared some data. If you want to load it into db. Use commands:
    ``` python
    python.exe .\manage.py loaddata .\fixtures\blog.json
    ```
    then
    ``` python
    python.exe .\manage.py loaddata .\fixtures\taggit.json
    ```
   
9. Run a project with followed command:
    ``` python
    python.exe .\manage.py runserver
    ```    
