def sentiment_annotation(data):
    # function to facilitate manual sentiment annotation of data
    # input: data as iterable: list of articles/ phrases/ words/ ...
    # output: dictionary with annotations in range (-1, 1)

    sentiment_dict = {}
    # translates input to numerical values
    translation = {'n': 1, 'p': 0, '': 2}  
    print("sentiment input: p = positive, n = negative, press enter if neutral:")
	
    for phrase in data:
        print(phrase)
        sentiment = input()
		
        #check for valid input
        while sentiment not in ["n", "p", ""]:
            print("no valid input: p = positive, n = negative, press enter if neutral: ")
            print(phrase)
            sentiment = input()		
        sentiment_dict[phrase] = translation[sentiment]
                           
    return sentiment_dict


if __name__ == "__main__":  
    # toy example
    data = ["Schutzsuchender", "Wirtschaftsflüchtling", "Geflüchteter"]
    dict = sentiment_annotation(data)
    print(dict)