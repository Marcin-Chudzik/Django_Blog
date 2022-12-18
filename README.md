# Blog App

This app is a simple example of a personal Blog, built in Python/Django.
I implemented there few functionalities such like:
- adding / removing posts
- tagging posts
- creating new tags
- commenting on posts
- search for the posts
- filtering posts by tags
- displaying similar posts for the reader.
- list of the mostly commented posts

## How to run

1. Using a GIT write the command.
```bash
git clone https://github.com/Marcin-Chudzik/Django_Blog.git
```

2. Install PostgreSQL.<br>
**!IMPORTANT!**<br> Default setting for project are wrote to work with PostgreSQL installed with the instruction from below.
If you change the admin username or password, please remember that they need to be changed later in the **Django_Blog/myblog/settings.py**.
<br>*Make a steps till **12** it's enough to run the project.*<br>
Link to the instruction how to install it correctly -> 
<a href="https://www.postgresql.r2schools.com/how-to-install-postgresql-11-and-pgadmin-on-windows-11/">PostgreSQL</a><br>

3. Create a new virtual environment.
Open a repository in the code editor (I'm using Pycharm).<br>
Open a terminal and being in the "Django_Blog" directory type a command:
```python
python.exe -m venv venv
```

4. Activate a new venv, change directory on "myblog" and use command.
```python
pip install -r requirements.txt
```
