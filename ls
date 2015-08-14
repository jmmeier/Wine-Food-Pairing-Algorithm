Justin Meier
CS221
Final Project

The two main components of the code are preprocessing and algorithm/model running.  The code itself
is in python so you can simply run the command "pythong algorithms.py" and the code will execute
by itself.

Preprocessing:
A large potion of the code involves transforming the datasets into a usable format and then
deriving certain features using a combination of the datasets.  These few functions are implemented at
the beginning of the code and will have comments above the function describing exactly what it does.
The main use of this is turning the data into dictionaries so that data about a specific food
or about a specific wine can be looked up more quickly.

Algorithm/Model Running
the next portion involved in the code are running Naive Bayes algorithm and running the versions 
of the K-Means and clustering algorithm.  If the function name does not incidate that the algorithm 
is finding a specific wine, then the algorithm is being used to predict the color of the wine.  
However, if the function name indicates that the algorithm is used for finding a specific score, 
then it is attempting to find the name of the best wine to pair with the dinner.

When the word "score" or "rate" or "rating" is used, this means the data being used for the algorithm
involves not simply the occurence of a wine and a food together, but also the rating as a way to weight
the occurences of wine and food pairings.




All of the functions have comments above them, describing exactly what the function is used for.  As well,
when running the code, a detailed description of the accuracy of every model variation is printed to the
consolse and gives the reader a good sense of how accurate the models are in comparison to each other.

Thank you very much for spending your time going through my code and grading my final report.  It is much
appreciated and I hope you are as excited about the results of the model as I am!