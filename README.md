# Arbitrage_Web_App
This is a full stack web app used for calculating and finding arbitrage sports betting opportunities. 
More information on it is in help.html within the templates folder. It uses Flask and Google cloud sql,
with a mySQL web database.
## Local Deployment
To locally run all you need to do is clone the repository and make sure you have all the dependencies in,
requirements.txt downloaded. Then just change the app.run function in ```main.py```to be 
```app.run(debug=True)```
After this all you need to do is make sure that the ```IS_LOCAL``` variable in  ```__init__.py``` is set to true, then run the ```main.py``` file.
## Struggles 
I am still working on deploying it using Google App Engine, mainly struggling with the use of Cloud SQL Auth Proxy,
but am continuing to work on this project and specifically deployment.
