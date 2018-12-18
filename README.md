Description of Project: An application that allows users to search for New York Times articles using keywords and create and update collections of NY Times articles. 

Routes: 
1. http://localhost:5000 --> "index.html"
2. http://localhost:5000/login --> "login.html"
3. http://localhost:5000/logout 
4. http://localhost:5000/register --> "register.html"
5. http://localhost:5000/secret
6. http://localhost:5000/articles_searched/search_term --> "searched_articles.html"
7. http://localhost:5000/search_terms --> "search_terms.html"
8. http://localhost:5000/create_collection --> "create_collection.html"
9. http://localhost:5000/collections --> "collections.html"
10. http://localhost:5000/collection/id_num --> "collection.html"
11. http://localhost:5000/collection/update/item --> "update_item.html"
12. http://localhost:5000/collection/delete/search_term  
13. http://localhost:5000/ajax --> 
14. http://localhost:5000/show-articles --> 

Code Citations and Other Sources of Help:  
1. https://github.com/sindhugiri/HW3/blob/master/SI364W18_HW3.py
2. https://github.com/SI364-FA18/Lecture9_SampleTwitterStoring/blob/master/SI364_twitterapp.py
3. https://github.com/SI364-FA18/Many-To-Many-Relationships/blob/master/main_app.py
4. http://jinja.pocoo.org/docs/2.10/templates/
5. https://stackoverflow.com/questions/23224889/whitespace-in-regular-expression
6. https://github.com/sindhugiri/HW4
7. https://github.com/sindhugiri/HW5


**1. Ensure that your SI364final.py file has all the setup (app.config values, import statements, code to run the app if that file is run, etc) necessary to run the Flask application, and the application runs correctly on http://localhost:5000 (and the other routes you set up). Your main file must be called SI364final.py, but of course you may include other files if you need.**

**2. A user should be able to load http://localhost:5000 and see the first page they ought to see on the application.**

**3. Include navigation in base.html with links (using a href tags) that lead to every other page in the application that a user should be able to click on. (e.g. in the lecture examples from the Feb 9 lecture, like this )**

**4. Ensure that all templates in the application inherit (using template inheritance, with extends) from base.html and include at least one additional block.**

**5. Must use user authentication (which should be based on the code you were provided to do this e.g. in HW4).**

**6. Must have data associated with a user and at least 2 routes besides logout that can only be seen by logged-in users.**

**7. At least 3 model classes besides the User class.**

**8. At least one one:many relationship that works properly built between 2 models.**

**9. At least one many:many relationship that works properly built between 2 models.**

**10. Successfully save data to each table.**

**11. Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for) and use it to effect in the application (e.g. won't count if you make a query that has no effect on what you see, what is saved, or anything that happens in the app).**

**12. At least one query of data using an .all() method and send the results of that query to a template.**

**13. At least one query of data using a .filter_by(... and show the results of that query directly (e.g. by sending the results to a template) or indirectly (e.g. using the results of the query to make a request to an API or save other data to a table).**

14. At least one helper function that is not a get_or_create function should be defined and invoked in the application.

**15. At least two get_or_create functions should be defined and invoked in the application (such that information can be saved without being duplicated / encountering errors).**

**16. At least one error handler for a 404 error and a corresponding template.**

**17. Include at least 4 template .html files in addition to the error handling template files.**

**18. At least one Jinja template for loop and at least two Jinja template conditionals should occur amongst the templates.**
 
**19. At least one request to a REST API that is based on data submitted in a WTForm OR data accessed in another way online (e.g. scraping with BeautifulSoup that does accord with other involved sites' Terms of Service, etc).**

**20. Your application should use data from a REST API or other source such that the application processes the data in some way and saves some information that came from the source to the database (in some way).**

**21. At least one WTForm that sends data with a GET request to a new page.**

**22. At least one WTForm that sends data with a POST request to the same page. (NOT counting the login or registration forms provided for you in class.)**

**23. At least one WTForm that sends data with a POST request to a new page. (NOT counting the login or registration forms provided for you in class.)**

**24. At least two custom validators for a field in a WTForm, NOT counting the custom validators included in the log in/auth code.**

**25. Include at least one way to update items saved in the database in the application (like in HW5).**

**26. Include at least one way to delete items saved in the database in the application (also like in HW5).**

**27. Include at least one use of redirect.**

**28. Include at least two uses of url_for. (HINT: Likely you'll need to use this several times, really.)**

29. Have at least 5 view functions that are not included with the code we have provided. (But you may have more!)

30. (100 points) Include a use of an AJAX request in your application that accesses and displays useful (for use of your application) data.

**31. (100 points) Create, run, and commit at least one migration. (We'll see this from the files generated and can check the history)**

32. (100 points) Deploy the application to the internet (Heroku) — only counts if it is up when we grade / you can show proof it is up at a URL and tell us what the URL is in the README. (Heroku deployment as we taught you is 100% free so this will not cost anything.)