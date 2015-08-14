
import copy;

# Read the databases that I currently have
wineDatabase = open('winelist', 'r');
database = open('database', 'r');
wineToFlavor = open('winetoflavor', 'r');
wineToDinner = open('winetodinner', 'r');
foods = database.readlines();
wines = wineDatabase.readlines();
wineFlavors = wineToFlavor.readlines();
dinners = wineToDinner.readlines();


# A list of food items my program supports
foodItems = list();

# A list of wines that pair with a food in my database where
# I currently do not have the wine
neededWines = list();

# A diciontary associating each food to a list of (wine, score) tupls
foodDictionary = dict();

# A dictionary associating each wine to its type (red, white, dessert) and location
wineDictionary = dict();

# Probability a given food should pair with a red wine, using various methods
# Experiental probabilities.  Did not use as were less successful than Bayes
nonBayesProbability = dict();
nonBayesProbabilityLaplace = dict();
nonBayesProbabilityPoints = dict();
nonBayesProbabilityPointsLaplace = dict();
 
# Probability of having a specific food, given a red wine, using various methods
bayesProbabilityRed = dict();
bayesProbabilityRedLaplace = dict();
bayesProbabilityRedPoints = dict();
bayesProbabilityRedPointsLaplace = dict();

# Probability of having a specific food, given a white wine, using various methods
bayesProbabilityWhite = dict();
bayesProbabilityWhiteLaplace = dict();
bayesProbabilityWhitePoints = dict();
bayesProbabilityWhitePointsLaplace = dict();

# Dictionary mapping each food to a dictionary of wines mapping each wine to a probability
probabilityTypeWineScore = dict();
probabilityTypeWineScoreLaplace = dict();
probabilityTypeWine = dict();
probabilityTypeWineLaplace = dict();

# Currently in progress, a mapping of each wine to its flavor palate
wineFlavorDictionary = dict();

# Dictionary mapping each food to its averaged wine flavor profile
foodFlavorDictionary = dict();

# Dictionary mapping each dinner to its averaged wine flavor profile
dinnerFlavorDictionary = dict();

# List of wines and the ingredients of the dinner that pair with the wine
dinnerDatabase = dict();

# List of the centroids.  This comes from the flavor profile database
centroidList = list();

averagePoints = 0;


#PRE-PROCESSING
# Creates the wine dictionary of having a wine and knowing the color and country
def createWineDictionary():
	for wine in wines:
		wine = wine.split();
		wineName = wine[0];
		wine.remove(wineName);
		wineDictionary[wineName] = wine;


# Creates a dictionary of a food item and a list of the wines that pair with
# said food item, including the rating.
def createFoodDictionary():
	for food in foods:
		foodData = food.split();
		foodName = foodData[0];
		data = (foodData[1], foodData[2]);
		if foodName in foodDictionary:
			currentData = foodDictionary[foodName];
			currentData.append(data);
			foodDictionary[foodName] = currentData;
		else:
			currentData = list();
			currentData.append(data);
			foodDictionary[foodName] = currentData;

# Creates the database of a specific wine, type of meal, and number of meal pairing
# to a list of ingredients that compose the dinner.
def DinnerDatabase():
	index = 0;
	for dinner in dinners:
		dinner = dinner.split();
		wineName = dinner[0];
		dinnerType = dinner[1];
		dinner.remove(wineName);
		dinner.remove(dinnerType);
		dinnerData = (dinnerType, wineName, index);
		dinnerDatabase[dinnerData] = dinner;
		index += 1			

# Create a dictoinary of a specific wine to its flavor profile
def createWineFlavorProfileDictionary():
	for wine in wineFlavors:
		data = wine.split();
		wineName = data[0];
		data.remove(wineName);
		flavorProfileInt = [float(x) for x in data];
		wineFlavorDictionary[wineName] = flavorProfileInt;

# Creates a list of centroids from the wine flavor profiles found
# in the flavor profile dataset
def createCentroidList():
	for wine in wineFlavorDictionary:
		flavorProfile = wineFlavorDictionary[wine];
		centroidList.append((wine, flavorProfile));

# Average together the flavor profiles of the wines associated with a food and
# create a dictionary associating the food with its flavor profile
def createFoodFlavorProfileDictionary():
	for food in foodDictionary:
		data = foodDictionary[food];
		numWines = 0;
		for wine in data:
			wineName = wine[0];
			if wineName in wineFlavorDictionary:
				numWines += 1;
				flavorProfile = wineFlavorDictionary[wineName];
				if food in foodFlavorDictionary:
					oldFlavorProfile = foodFlavorDictionary[food];
					newFlavorProfile = list();
					for i in range(len(oldFlavorProfile)):
						summedFlavor = flavorProfile[i] + oldFlavorProfile[i];
						newFlavorProfile.insert(i, summedFlavor);
					foodFlavorDictionary[food] = newFlavorProfile;
				else:
					foodFlavorDictionary[food] = flavorProfile;
		if food in foodFlavorDictionary:
			averagedFlavorProfile = [x / numWines for x in foodFlavorDictionary[food]];
			foodFlavorDictionary[food] = averagedFlavorProfile;

# Average together the flavor profiles of the ingredients found within the dinner
# and create a dictionary associating the dinner with its flavor profile.
def createDinnerFlavorProfileDictionary():
	foodFlavorDictionaryForDinner = copy.deepcopy(foodFlavorDictionary);
	print "Running K-Means Algorithm on Dinner";
	kmeansDictionary = dict();
	for dinner in dinnerDatabase:
		averagedFlavorProfile = None;
		ingredients = dinnerDatabase[dinner];
		numIngredients = 0;
		for ingredient in ingredients:
			numIngredients += 1;
			if ingredient in foodFlavorDictionary:
				flavorProfile = copy.deepcopy(foodFlavorDictionary[ingredient]);
				if averagedFlavorProfile == None:
					averagedFlavorProfile = flavorProfile;
				else:
					for i in range(len(flavorProfile)):
						averagedFlavorProfile[i] += flavorProfile[i];
		if averagedFlavorProfile != None:
			averagedFlavorProfile = [x / numIngredients for x in averagedFlavorProfile];
			dinnerFlavorDictionary[dinner] = averagedFlavorProfile;


# Go through the database and calculat the probability that given a specific
# color of wine, you have a specific type of ingredient.  This is done for each ingredient.
# I attempted to calcualte the probabilities in a slightly different way as well, but the
# accuracy of this was less than the accuracy achieved with the calculated Bayes probability
# so I decided to not include this in the final paper.
def PercentageRedAndWhite():
	totalRed = 0; # Used for no rating consideration
	totalWhite = 0;
	totalRedPoints = 0; # Used for rating consideration
	totalWhitePoints = 0;
	for food in foodDictionary:
		data = foodDictionary[food];
		for wine in data:
			wineName = wine[0];
			wineScore = float(wine[1]);
			if wineName in wineDictionary:
				wineType = wineDictionary[wineName][0];
				if wineType == "red":
					totalRed += 1;
					totalRedPoints += wineScore;
				if wineType == "white":
					totalWhite += 1;
					totalWhitePoints += wineScore;
	# Used for Laplace smoothing as the smoothing paramter
	averagePoints = (totalRedPoints + totalWhitePoints) / (totalRed + totalWhite);


	for food in foodDictionary:
		foodItems.append(food);
		redPoints = 0.0; #U sed for rating consideration
		whitePoints = 0.0;
		red = 0.0; # Used for no rating consideration
		white = 0.0;
		data = foodDictionary[food];
		for wine in data:
			wineName = wine[0];
			wineScore = float(wine[1]);
			if wineName in wineDictionary:
				wineData = wineDictionary[wineName];
				if wineData[0] == 'white':
					whitePoints = whitePoints + wineScore;
					white += 1;
				if wineData[0] == 'red':
					redPoints = redPoints + wineScore;
					red += 1;
			else:
				if wineName not in neededWines:
					neededWines.append(wineName);
		if red == 0 and white == 0:
			nonBayesProbability[food] = 0.0;
			nonBayesProbabilityPoints[food]  = 0.0;	
		else:
			nonBayesProbability[food] = red / (red + white);
			nonBayesProbabilityPoints[food] = red / (red + white);

		# Calculate dprobabilities WITHOUT Laplace Smoothing
		bayesProbabilityRed[food] = red / totalRed;
		bayesProbabilityWhite[food] = white / totalWhite;
		bayesProbabilityRedPoints[food] = redPoints / totalRedPoints;
		bayesProbabilityWhitePoints[food] = whitePoints / totalWhitePoints;

		# Calculated probabilities WITH Laplace Smoothing
		redPoints += averagePoints;
		whitePoints += averagePoints;
		nonBayesProbabilityLaplace[food] = (red + 1) / (red + white + 2);
		nonBayesProbabilityPointsLaplace[food] = (redPoints + averagePoints) / (redPoints + whitePoints + (2 * averagePoints));
		bayesProbabilityRedLaplace[food] = (red + 1) / (totalRed + 2);
		bayesProbabilityWhiteLaplace[food] = (white + 1) / (totalWhite + 2);
		bayesProbabilityRedPointsLaplace[food] = (redPoints  + averagePoints) / (totalRedPoints + (2 * averagePoints));
		bayesProbabilityWhitePointsLaplace[food] = (whitePoints + averagePoints) / (totalWhitePoints + (2 * averagePoints));


# Go through the database and calculates the probability that given a specific
# color of wine, you have a specific type of ingredient.  This is done for each ingredient.
def PercentageForEachTypeOfWine():
	totalCountForWine = dict();
	for food in foodDictionary:
		data = foodDictionary[food];
		for wine in data:
			wineName = wine[0];
			if wineName not in totalCountForWine:
				totalCountForWine[wineName] = float(wine[1]);
			else:
				totalCountForWine[wineName] += float(wine[1]);
	for food in foodDictionary:
		data = foodDictionary[food];
		totalWineScore = 0;
		probabilityOfWineScore = dict();
		probabilityOfWine = dict();
		for wine in data:
			wineName = wine[0];
			wineScore = float(wine[1]);
			totalWineScore += wineScore;
			if wineName in probabilityOfWine:
				probabilityOfWineScore[wineName] += totalWineScore;
				probabilityOfWine[wineName] += 1;
			else:
				probabilityOfWineScore[wineName] = totalWineScore;
				probabilityOfWine[wineName] = 1;
		probabilityOfWineScoreLaplace = copy.deepcopy(probabilityOfWineScore);
		probabilityOfWineLaplace = copy.deepcopy(probabilityOfWine);


		totalNumberWines = len([x for x in probabilityOfWineLaplace]);
		for wine in probabilityOfWineLaplace:
			probabilityOfWineScoreLaplace[wine] = float(probabilityOfWineScoreLaplace[wine] + averagePoints) / totalWineScore + (averagePoints * totalNumberWines);
			probabilityOfWineLaplace[wine] = float(probabilityOfWineLaplace[wine]) + 1 / totalCountForWine[wine] + totalNumberWines;
		for wine in probabilityOfWineScore:
			probabilityOfWineScore[wine] = float(probabilityOfWineScore[wine]) / totalWineScore;
			probabilityOfWine[wine] = float(probabilityOfWine[wine]) / totalCountForWine[wine];


		probabilityTypeWineScore[food] = probabilityOfWineScore;
		probabilityTypeWine[food] = probabilityOfWine;


#ALGORITHMS AND MODELS

# Runs Naive Bayes algorithm using its four variants.  These four variants are determined by 
# Whether Laplace smoothing is used or unused and whether rating consideration is used or
# unused.  This Naive Bayes is specifically attempting to predict the color of the wine
def NaiveBayes(score, laplace):
	if laplace == False and score == False:
		print "Running Naive Bayes Testing with NO Laplace and NO score consideration";
	if laplace == True and score == False:
		print "Running Naive Bayes Testing WITH Laplace and NO score consideration";
	if laplace == False and score == True:
		print "Running Naive Bayes Testing with NO Laplace and WITH score consideration";
	if laplace == True and score == True:
		print "Running Naive Bayes Testing WITH Laplace and WITH score consideration";

	totalRed = 0.0;
	totalWhite = 0.0;
	correctRed = 0;
	correctWhite = 0;

	for dinner in dinnerDatabase:
		ingredients = dinnerDatabase[dinner];
		red = 1.0;
		white = 1.0;
		if laplace == False and score == False:
			for ingredient in ingredients:
				if ingredient in bayesProbabilityRed:
					red *= bayesProbabilityRed[ingredient];
					white *= bayesProbabilityWhite[ingredient];
		if laplace == True and score == False:
			for ingredient in ingredients:
				if ingredient in bayesProbabilityRedLaplace:
					red *= bayesProbabilityRedLaplace[ingredient];
					white *= bayesProbabilityWhiteLaplace[ingredient];
		if laplace == False and score == True:
			for ingredient in ingredients:
				if ingredient in bayesProbabilityRedPoints:
					red *= bayesProbabilityRedPoints[ingredient];
					white *= bayesProbabilityWhitePoints[ingredient];
		if laplace == True and score == True:
			for ingredient in ingredients:
				if ingredient in bayesProbabilityRedPointsLaplace:
					red *= bayesProbabilityRedPointsLaplace[ingredient];
					white *= bayesProbabilityWhitePointsLaplace[ingredient];

		#Create accuracy information to print
		predictedWineType = "";
		if red > white:
			predictedWineType = "red";
		else:
			predictedWineType = "white";
		wineData = wineDictionary[dinner[1]];
		actualWineType = wineData[0];

		if actualWineType == "red":
			totalRed += 1;
			if actualWineType == predictedWineType:
				correctRed += 1;
		if actualWineType == "white":
			totalWhite += 1;
			if actualWineType == predictedWineType:
				correctWhite += 1;
	print "Total number of red wines was: " + str(totalRed);
	print "You correctly predicted a red wine with the probability of " + str(correctRed / totalRed);
	print "Total number of white wines was: " + str(totalWhite);
	print "You correctly predicted a white wine with the probability of " + str(correctWhite / totalWhite);
	print "Your total prediction accurary is : " + str((correctRed + correctWhite) / (totalRed + totalWhite));
	print "";



# Runs Naive Bayes algorithm using its four variants.  These four variants are determined by 
# Whether Laplace smoothing is used or unused and whether rating consideration is used or
# unused.  This Naive BAyes is attempting to predict a specific type of wine.  The variable
# numTopWines indicates the number of top predicted wines it should keep track of.  It then
# determines accuracy based on whether the correct wine is found within that list.
def NaiveBayesSpecificWine(numTopWines, score, laplace):
	if laplace == False and score == False:
		print "Running Naive Bayes with NO Laplace and NO Score consideration looking at the top " + str(numTopWines) + " wines";
	if laplace == True and score == False:
		print "Running Naive Bayes WITH Laplace and NO Score consideration looking at the top " + str(numTopWines) + " wines";
	if laplace == False and score == True:
		print "Running Naive Bayes with NO Laplace and WITH Score consideration looking at the top " + str(numTopWines) + " wines";
	if laplace == True and score == True:
		print "Running Naive Bayes WITH Laplace and WITH Score consideration looking at the top " + str(numTopWines) + " wines";


	totalDinner = 0.0;
	numSuccesses = 0.0;
	for dinner in dinnerDatabase:
		ingredients = dinnerDatabase[dinner];
		bestWineForMealDictionary = dict();
		for ingredient in ingredients:


			if laplace == False and score == False:
				if ingredient in probabilityTypeWine:
					bestWineForIngredientDictionary = probabilityTypeWine[ingredient];
			if laplace == True and score == False:
				if ingredient in probabilityTypeWineLaplace:
					bestWineForIngredientDictionary = probabilityTypeWineLaplace[ingredient];
			if laplace == False and score == True:
				if ingredient in probabilityTypeWineScore:
					bestWineForIngredientDictionary = probabilityTypeWineScore[ingredient];
			if laplace == True and score == True:
				if ingredient in probabilityTypeWineScoreLaplace:
					bestWineForIngredientDictionary = probabilityTypeWineScoreLaplace[ingredient];


			if ingredient in probabilityTypeWineScore:
				bestWineForIngredientDictionary = probabilityTypeWineScore[ingredient];
				for wine in wineDictionary:
					if wine in bestWineForIngredientDictionary:
						probability = bestWineForIngredientDictionary[wine];
						if wine in bestWineForMealDictionary:
							data = bestWineForMealDictionary[wine];
							bestWineForMealDictionary[wine] = data * probability;
						else:
							bestWineForMealDictionary[wine] = probability;

		wineList = list();
		winePercentList = list();
		for key in bestWineForMealDictionary:
			wineList.append((key, bestWineForMealDictionary[key]));
			winePercentList.append(bestWineForMealDictionary[key]);
		if dinner[1] in bestWineForMealDictionary:
			totalDinner += 1;

		#Create accuracy informationt o print
		bestWineList = list();
		iters = 0;
		while len(bestWineList) < numTopWines:
			iters += 1;
			if len(winePercentList) > 0:
				maxValue = max(winePercentList);
				winePercentList.remove(maxValue);
				for wine in wineList:
					if wine[1] == maxValue:
						bestWineList.append(wine[0]);
						wineList.remove(wine);
			if iters > 100:
				break;
			else:
				iters += 1;
		if dinner[1] in bestWineList or len(bestWineList) == 0:
			numSuccesses += 1;


	print "Total Dinnners: " + str(totalDinner);
	print "PredictionAccurary: " + str(numSuccesses / totalDinner);
	print "";



# Runs the k_Means algorithm on the food given in the first dataset.  That is, the first
# dataset contains a specific food paired with a specific wine.  This algorithm checks
# the accuracy of the predicted wine given a specific food when we are using the
# averaged flavor profile as the new variable upon which to base the prediction
def kMeansAlgorithmFood(iters):
	print "Running K-Means Algorithm on Food";
	foodFlavorDictionaryForUse = copy.deepcopy(foodFlavorDictionary);

	# No converge so changed the number of iterations
	for i in range(iters):
		kmeansDictionary = dict();
		for food in foodDictionary:
			if food in foodFlavorDictionaryForUse:
				foodFlavorProfile = foodFlavorDictionaryForUse[food];
				smallestDistance = None;
				smallestDistanceWine = "";
				for wine in centroidList:
					wineFlavorProfile = wine[1];
					distance = 0;
					for i in range(len(wineFlavorProfile)):
						distance += (wineFlavorProfile[i] - foodFlavorProfile[i]) **2;
					if smallestDistance == None:
						smallestDistance = distance;
						smallestDistanceWine = wine[0];
					elif distance < smallestDistance:
						smallestDistance = distance
						smallestDistanceWine = wine[0];
				kmeansDictionary[food] = smallestDistanceWine;

		# Change the centroids after all foods have been assigned to them
		newCentroidList = list();
		for wine in centroidList:
			wineName = wine[0];
			totalInCentroid = 0;
			flavorProfile = None;
			for food in kmeansDictionary:
				if kmeansDictionary[food] == wineName:
					totalInCentroid += 1;
					if flavorProfile == None:
						flavorProfile = foodFlavorDictionaryForUse[food];
					else:
						newFlavorProfile = foodFlavorDictionaryForUse[food];
						for i in range(len(newFlavorProfile)):
							flavorProfile[i] += newFlavorProfile[i];
			if flavorProfile is not None:
				flavorProfile = [x / totalInCentroid for x in flavorProfile];
			else:
				flavorProfile = wineFlavorDictionary[wineName];
			newCentroidList.append((wineName, flavorProfile));



	# Create accuracy information to print
	totalFood = 0.0;
	accuratelyPredictedFood = 0.0;
	predictedWhiteWine = 0.0;
	predictedRedWine = 0.0;
	totalRedWine = 0.0;
	totalWhiteWine = 0.0;
	for food in kmeansDictionary:
		totalFood += 1;
		predictedWineName = kmeansDictionary[food];
		accurateWineType = "";
		if bayesProbabilityRedLaplace[food] < bayesProbabilityWhiteLaplace[food]:
			accurateWineType = "white";
			totalWhiteWine += 1;
		else:
			accurateWineType = "red";
			totalRedWine += 1;
		wineData = wineDictionary[predictedWineName];
		predictedWineType = wineData[0];
		if accurateWineType == predictedWineType:
			accuratelyPredictedFood += 1;
			if accurateWineType == "red":
				predictedRedWine += 1;
			elif accurateWineType == "white":
				predictedWhiteWine += 1;

	print "Ran k-means a total of " + str(iters) + " times";
	print "Total number of foods: " + str(totalFood);
	print "Accurately predicted: " + str(accuratelyPredictedFood);
	print "White Wine Prediction Accurary: " + str(predictedWhiteWine / totalWhiteWine);
	print "Red Wine Prediction Accurary: " + str(predictedRedWine / totalRedWine);
	print "Prediction accurary: " + str(accuratelyPredictedFood / totalFood);
	print "";



# Runs the K-Means algorithm on a list of ingredients which represents a dinner.
# Predicts the color of the wine to pair with the dinner based on the color of the
# centroid it converged upon, where each centroid is one of the 32 original flavor
# profiles of wines in the database.
def kMeansAlgorithmDinner(iters):
	print "Running K-Means Algorithm on Dinners";
	dinnerFlavorDictionaryForUse = copy.deepcopy(dinnerFlavorDictionary);

	# Wouldn't converge.  Changed the number of iterations
	for i in range(iters):
		kmeansDictionary = dict();
		for dinner in dinnerFlavorDictionaryForUse:
			if dinner in dinnerFlavorDictionaryForUse:
				dinnerFlavorProfile = dinnerFlavorDictionaryForUse[dinner];
				smallestDistance = None;
				smallestDistanceWine = "";
				for wine in centroidList:
					wineFlavorProfile = wine[1];
					distance = 0.0;
					for i in range(len(wineFlavorProfile)):
						distance += (float(wineFlavorProfile[i]) - float(dinnerFlavorProfile[i])) **2;
					if smallestDistance == None:
						smallestDistance = distance;
						smallestDistanceWine = wine[0];
					elif distance < smallestDistance:
						smallestDistance = distance
						smallestDistanceWine = wine[0];
				kmeansDictionary[dinner] = smallestDistanceWine;

		#Update the centroids now that every dinner has been clustered with one
		newCentroidList = list();
		for wine in centroidList:
			wineName = wine[0];
			totalInCentroid = 0.0;
			flavorProfile = None;
			for dinner in kmeansDictionary:
				if kmeansDictionary[dinner] == wineName:
					totalInCentroid += 1;
					if flavorProfile == None:
						flavorProfile = dinnerFlavorDictionaryForUse[dinner];
					else:
						newFlavorProfile = dinnerFlavorDictionaryForUse[dinner];
						for i in range(len(newFlavorProfile)):
							flavorProfile[i] += newFlavorProfile[i];
			if flavorProfile is not None:
				flavorProfile = [x / totalInCentroid for x in flavorProfile];	
				newCentroidList.append((wineName, flavorProfile));



	# Create accuracy information to print
	totalDinner = 0.0;
	accuratelyPredictedDinner = 0.0;
	predictedWhiteWine = 0.0;
	predictedRedWine = 0.0;
	totalRedWine = 0.0;
	totalWhiteWine = 0.0;
	for dinner in kmeansDictionary:
		totalDinner += 1;
		predictedWineName = kmeansDictionary[dinner];
		accurateWine = dinner[1];
		accurateWineType = wineDictionary[accurateWine][0];
		if accurateWineType == "red":
			totalRedWine += 1;
		elif accurateWineType == "white":
			totalWhiteWine += 1;
		wineData = wineDictionary[predictedWineName];
		predictedWineType = wineData[0];
		if accurateWineType == predictedWineType:
			accuratelyPredictedDinner += 1;
			if accurateWineType == "red":
				predictedRedWine += 1;
			elif accurateWineType == "white":
				predictedWhiteWine += 1;
	print "Ran k-means a total of " + str(iters) + " times";
	print "Total number of dinners: " + str(totalDinner);
	print "Accurately predicted: " + str(accuratelyPredictedDinner);
	print "White Wine Prediction Accurary: " + str(predictedWhiteWine / totalWhiteWine);
	print "Red Wine Prediction Accurary: " + str(predictedRedWine / totalRedWine);
	print "Prediction accurary: " + str(accuratelyPredictedDinner / totalDinner);
	print "";


# Runs the K-Means algorithm, attempting to find a specific wine.  The other K-Means algorithms had
# their accuracies maximized with a single iteration and I decided to only do a single iterations of
# the algorithm before deciding on the prediction.  The variable numTopWines indicates the number of
# top predicted wines the algorithm should keep track of.  The accuracy is then determined by whether
# the correct wine is found within that list.
def kMeansAlgorithmSpecificWine(numTopWines):
	print "Running K-Means Algorithm on Dinner and Finding the top " + str(numTopWines) + " wines";
	dinnerFlavorDictionaryForUse = copy.deepcopy(dinnerFlavorDictionary);
	totalDinner = 0.0;
	accuratelyPredictedDinner = 0.0;
	for dinner in dinnerFlavorDictionaryForUse:
		totalDinner += 1;
		predictedWine = dinner[1];
		kmeansDictionary = dict();
		dinnerFlavorProfile = dinnerFlavorDictionaryForUse[dinner];
		differences = dict();
		for wine in centroidList:
			wineFlavorProfile = wine[1];
			difference = 0;
			for i in range(len(wine[1])):
				difference += (dinnerFlavorProfile[i] - wineFlavorProfile[i]) **2;
			differences[wine[0]] = difference;

		topWines = list();
		differenceValues = [differences[x] for x in differences];
		iters = 0;
		while len(topWines) < numTopWines:
			iters += 1;
			if len(differenceValues) != 0:
				minDistance = min(differenceValues);
				differenceValues.remove(minDistance);
				for wine in differences:
					if minDistance == differences[wine]:
						topWines.append(wine);
			if iters == 100:
				break;
		if predictedWine in topWines:
			accuratelyPredictedDinner += 1;


	print "Total number of dinners: " + str(totalDinner);
	print "Accruately predicted: " + str(accuratelyPredictedDinner);
	print "Prediction Accuracy: " + str(accuratelyPredictedDinner / totalDinner);
	print "";


# Runs an alternative approach to predicting the correct color of the wine.  Rather than having
# 32 centroids, the algorithm computer the averaged white wine flavor profile and the averaged
# red wine flavor profile and uses these as the centroids to determine what color of wine to
# predict.
def redVsWhiteWithAveragedFlavor():
	print "Running redvsWhiteWithFlavor";
	redFlavorProfile = None;
	whiteFlavorProfile = None;
	totalRed = 0.0;
	totalWhite = 0.0;
	for wine in centroidList:
		wineName = wine[0];
		flavorProfile = wine[1];
		wineType = wineDictionary[wineName][0];
		if wineType == "red":
			totalRed += 1;
			if redFlavorProfile == None:
				redFlavorProfile = flavorProfile;
			else:
				for i in range(len(flavorProfile)):
					redFlavorProfile[i] += flavorProfile[i];
		if wineType == "white":
			totalWhite += 1;
			if whiteFlavorProfile == None:
				whiteFlavorProfile = flavorProfile;
			else:
				for i in range(len(flavorProfile)):
					whiteFlavorProfile[i] += flavorProfile[i];
	redFlavorProfile = [x / totalRed for x in redFlavorProfile];
	whiteFlavorProfile = [x / totalWhite for x in whiteFlavorProfile];

	#Accuracy information to print
	totalDinner = 0.0;
	correctlyPredicted = 0.0;
	totalRed = 0.0
	totalWhite = 0.9
	correctRed = 0.0
	correctWhite = 0.0
	for dinner in dinnerFlavorDictionary:
		totalDinner += 1;
		correctWineType = wineDictionary[dinner[1]][0];
		differenceRed = 0;
		differenceWhite = 12;
		dinnerFlavorProfile = dinnerFlavorDictionary[dinner];
		for i in range(len(dinnerFlavorProfile)):
			differenceRed += (dinnerFlavorProfile[i] - redFlavorProfile[i]) **2;
			differenceWhite += (dinnerFlavorProfile[i] - whiteFlavorProfile[i]) **2;
		if differenceWhite > differenceRed and correctWineType == "red":
			correctlyPredicted += 1;
			correctRed += 1;
		if differenceWhite < differenceRed and correctWineType == "white":
			correctlyPredicted += 1;
			correctWhite += 1;
		if correctWineType == "red":
			totalRed += 1;
		if correctWineType == "white":
			totalWhite += 1;

	print "Total dinners was: " + str(totalDinner);
	print "Correct red was: " + str(correctRed / totalRed);
	print "Correct white was: " + str(correctWhite / totalWhite);
	print "Corectly predicted: " + str(correctlyPredicted / totalDinner);
	print "";


# Fun prompted entry function that allows the user to put in the ingredients of
# a dinner, one per line, and then see what color of wine to predict.
def PromptedEntry():
	# General promping questions for the user
	while(True):
		ingredients = list();
		print "Enter each ingredient and hit enter or type 'Done' if you are done";
		ingredient = raw_input();
		while ingredient != "Done":
			ingredient = raw_input();
			if ingredient == "Done":
				break;
			if ingredient not in foodDictionary:
				print "We do not have that ingredient yet.  Try another";
			else:
				ingredients.append(ingredient);

		probRed = 1;
		probWhite = 1	
		for ingredient in ingredients:
			probWhite = bayesProbabilityWhiteLaplace[ingredient];
			probRed = bayesProbabilityRedLaplace[ingredient];
		if probRed > probWhite:
			print "You should have a RED WINE";
		else:
			print "You should have a WHITE WINE";


# Creates the databases
createWineDictionary();
createFoodDictionary();
createWineFlavorProfileDictionary();
createFoodFlavorProfileDictionary();
createCentroidList();
PercentageRedAndWhite();
PercentageForEachTypeOfWine();
DinnerDatabase();
createDinnerFlavorProfileDictionary();

# Runs the algorithms
NaiveBayes(False, False);
NaiveBayes(False, True);
NaiveBayes(True, False);
NaiveBayes(True, True);
print "";
print "";
print "";
NaiveBayesSpecificWine(1, False, True);
NaiveBayesSpecificWine(2, False, True);
NaiveBayesSpecificWine(3, False, True);
NaiveBayesSpecificWine(4, False, True);
NaiveBayesSpecificWine(5, False, True);
NaiveBayesSpecificWine(6, False, True);
NaiveBayesSpecificWine(7, False, True);
NaiveBayesSpecificWine(8, False, True);
NaiveBayesSpecificWine(9, False, True);
NaiveBayesSpecificWine(10, False, True);
NaiveBayesSpecificWine(15, False, True);
NaiveBayesSpecificWine(20, False, True);
NaiveBayesSpecificWine(30, False, True);
print "";
print "";
print "";
kMeansAlgorithmFood(1);
kMeansAlgorithmFood(5);
kMeansAlgorithmFood(10);
kMeansAlgorithmFood(20);
kMeansAlgorithmFood(50);
print "";
print "";
print "";
kMeansAlgorithmDinner(1);
kMeansAlgorithmDinner(5);
kMeansAlgorithmDinner(10);
kMeansAlgorithmDinner(20);
kMeansAlgorithmDinner(50);
print "";
print "";
print "";
redVsWhiteWithAveragedFlavor();
print "";
print "";
print "";
kMeansAlgorithmSpecificWine(1);
kMeansAlgorithmSpecificWine(2);
kMeansAlgorithmSpecificWine(3);
kMeansAlgorithmSpecificWine(4);
kMeansAlgorithmSpecificWine(5);
kMeansAlgorithmSpecificWine(6);
kMeansAlgorithmSpecificWine(7);
kMeansAlgorithmSpecificWine(8);
kMeansAlgorithmSpecificWine(9);
kMeansAlgorithmSpecificWine(10);
kMeansAlgorithmSpecificWine(15);
kMeansAlgorithmSpecificWine(20);
kMeansAlgorithmSpecificWine(25);
kMeansAlgorithmSpecificWine(30);


#PromptedEntry();





